import asyncio
import datetime
import fcntl
import logging
import os
import pathlib
import socket
import subprocess
import sys
import uuid

from eurybis.config import DestinationEurybisConfiguration

LOGGER = logging.getLogger(__name__)


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


async def wait_until_readable(fileno: int):
    loop = asyncio.get_running_loop()
    ready = asyncio.Event()

    def on_readable():
        ready.set()

    loop.add_reader(fileno, on_readable)
    await ready.wait()


async def handle_file(
    sock: socket.socket, destination_directory: pathlib.Path, splice_pipe_size: int
):
    new_connection_start = datetime.time
    LOGGER.info("Handling new socket connection")
    sock.setblocking(True)

    rpipe, wpipe = os.pipe()

    size = int(pathlib.Path("/proc/sys/fs/pipe-max-size").read_text())
    fcntl.fcntl(wpipe, fcntl.F_SETPIPE_SZ, size)
    fcntl.fcntl(rpipe, fcntl.F_SETPIPE_SZ, size)

    os.set_blocking(rpipe, False)
    os.set_blocking(wpipe, False)

    filepath = destination_directory / str(uuid.uuid4())
    dest_file = filepath.open("wb", buffering=0)

    bytes_transferred = 0
    try:
        while True:
            byte_count_from_socket = os.splice(sock.fileno(), wpipe, size)
            if not byte_count_from_socket:
                break
            byte_count_from_pipe = os.splice(
                rpipe, dest_file.fileno(), byte_count_from_socket
            )
            bytes_transferred += byte_count_from_pipe
    finally:
        LOGGER.info("Closing socket, pipes and file")
        os.close(rpipe)
        os.close(wpipe)
        dest_file.close()
        sock.close()
    transfer_duration = datetime.datetime.now() - new_connection_start

    LOGGER.info(
        "Finished a transfer at %s",
        sizeof_fmt(bytes_transferred / transfer_duration.seconds, "B/s"),
    )


async def _receiver_server(config: DestinationEurybisConfiguration):
    config.lidir_socket_path.unlink(missing_ok=True)
    lidi_dest_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    lidi_dest_socket.bind(str(config.lidir_socket_path))
    lidi_dest_socket.setblocking(False)
    lidi_dest_socket.listen()
    LOGGER.info("Starting lidi")
    subprocess.Popen(
        (
            "diode-receive",
            f"--from={config.lidir_listen_host}:{config.lidir_listen_port}",
            f"--to-unix={config.lidir_socket_path}",
            f"--max-clients={config.lidir_max_clients}",
            # "--flush",
            "--decode-threads=5",
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
            handle_file(client_sock, config.data_directory, config.pipe_size)
        )


def destination_server(config: DestinationEurybisConfiguration):
    asyncio.run(
        _receiver_server(
            config,
        )
    )
