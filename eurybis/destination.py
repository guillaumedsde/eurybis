import asyncio
import fcntl
import logging
import os
import pathlib
import socket
import subprocess
import sys
import uuid

from eurybis.config import DestinationEurybisConfiguration
from eurybis.utils import BandwidthCounter, compute_pipe_size

LOGGER = logging.getLogger(__name__)


async def wait_until_readable(fileno: int):
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    def reader():
        loop.remove_reader(fileno)
        future.set_result(None)

    loop.add_reader(fileno, reader)
    await future


async def wait_until_writable(fileno: int):
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    def writer():
        loop.remove_writer(fileno)
        future.set_result(None)

    loop.add_writer(fileno, writer)
    await future


def _handle_file(
    sock: socket.socket, destination_directory: pathlib.Path, splice_pipe_size: int
):
    return asyncio.run(handle_file(sock, destination_directory, splice_pipe_size))


async def handle_file(
    sock: socket.socket, destination_directory: pathlib.Path, splice_pipe_size: int
):
    with BandwidthCounter() as bc:
        LOGGER.info("Handling new socket connection")
        sock.setblocking(False)

        rpipe, wpipe = os.pipe()

        size = splice_pipe_size
        fcntl.fcntl(wpipe, fcntl.F_SETPIPE_SZ, size)
        fcntl.fcntl(rpipe, fcntl.F_SETPIPE_SZ, size)

        os.set_blocking(rpipe, False)
        os.set_blocking(wpipe, False)

        filepath = destination_directory / str(uuid.uuid4())
        dest_file = filepath.open("wb", buffering=size)

        try:
            while True:
                await asyncio.gather(
                    wait_until_readable(sock.fileno()), wait_until_writable(wpipe)
                )
                byte_count_from_socket = os.splice(sock.fileno(), wpipe, size)
                if not byte_count_from_socket:
                    break
                await wait_until_readable(rpipe)
                byte_count_from_pipe = os.splice(
                    rpipe, dest_file.fileno(), byte_count_from_socket
                )
                bc.byte_count += byte_count_from_pipe
        finally:
            LOGGER.info("Closing socket, pipes and file")
            os.close(rpipe)
            os.close(wpipe)
            dest_file.close()
            sock.close()

        LOGGER.info("Finished a transfer at %s", bc.hf_bandwidth)


async def _receiver_server(config: DestinationEurybisConfiguration):
    config.lidir_socket_path.unlink(missing_ok=True)
    lidi_dest_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    lidi_dest_socket.setsockopt(
        socket.SOL_SOCKET, socket.SO_RCVBUF, compute_pipe_size(config.lidi_max_clients)
    )
    lidi_dest_socket.bind(str(config.lidir_socket_path))
    lidi_dest_socket.setblocking(False)
    lidi_dest_socket.listen()
    LOGGER.info("Starting lidi")
    subprocess.Popen(
        (
            "diode-receive",
            f"--from={config.lidir_listen_host}:{config.lidir_listen_port}",
            f"--to-unix={config.lidir_socket_path}",
            f"--max-clients={config.lidi_max_clients}",
            "--decode-threads=5",
            "--flush",
            "--cpu-affinity",
        ),
        stderr=sys.stderr,
        stdout=sys.stdout,
    )

    loop = asyncio.get_running_loop()

    LOGGER.info("Listening for connections on %s", config.lidir_socket_path)
    while True:
        client_sock, _ = await loop.sock_accept(lidi_dest_socket)
        asyncio.create_task(
            asyncio.to_thread(
                _handle_file,
                client_sock,
                config.data_directory,
                compute_pipe_size(config.lidi_max_clients),
            )
        )


def destination_server(config: DestinationEurybisConfiguration):
    asyncio.run(
        _receiver_server(
            config,
        )
    )
