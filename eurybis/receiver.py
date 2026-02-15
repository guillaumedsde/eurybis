import argparse
import asyncio
import logging
import os
import pathlib
import socket
import subprocess
import sys
import uuid

LOGGER = logging.getLogger(__name__)

BUF_SIZE = 1 << 20  # 1 MB


async def wait_until_readable(fileno: int):
    loop = asyncio.get_running_loop()
    ready = asyncio.Event()

    def on_readable():
        ready.set()

    loop.add_reader(fileno, on_readable)
    await ready.wait()


async def handle_file(sock: socket.socket, addr: str):
    LOGGER.info("Handling new socket connection")
    sock.setblocking(False)

    rpipe, wpipe = os.pipe()

    # os.set_blocking(rpipe, False)
    # os.set_blocking(wpipe, False)

    filepath = DATA_DIRECTORY / str(uuid.uuid4())
    dest_file = filepath.open("wb", buffering=0)

    try:
        while True:
            try:
                byte_count_from_socket = os.splice(sock.fileno(), wpipe, BUF_SIZE)
                if not byte_count_from_socket:
                    break
                LOGGER.debug("Spliced %d bytes from socket", byte_count_from_socket)
                byte_count_from_pipe = os.splice(
                    rpipe, dest_file.fileno(), byte_count_from_socket
                )
                LOGGER.debug("Spliced %d bytes from pipe", byte_count_from_pipe)
            except BlockingIOError:
                LOGGER.debug("BlockingIOError")
                await wait_until_readable(sock.fileno())
    finally:
        LOGGER.info("Closing socket, pipes and file")
        os.close(rpipe)
        os.close(wpipe)
        dest_file.close()
        sock.close()


async def _receiver_server(listen_address: str, listen_port: int):
    SOCKET_PATH.unlink(missing_ok=True)
    lidi_dest_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    lidi_dest_socket.bind(str(SOCKET_PATH))
    lidi_dest_socket.setblocking(False)
    lidi_dest_socket.listen()
    LOGGER.info("Starting lidi")
    subprocess.Popen(
        (
            "diode-receive",
            f"--from={listen_address}:{listen_port}",
            f"--to-unix={SOCKET_PATH}",
        ),
        stderr=sys.stderr,
        stdout=sys.stdout,
    )

    loop = asyncio.get_running_loop()

    LOGGER.info("Listening for connections on %s", SOCKET_PATH)
    while True:
        client_sock, client_addr = await loop.sock_accept(lidi_dest_socket)
        asyncio.create_task(handle_file(client_sock, client_addr))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="eurybis-receive",
        description="Receiver for Eurybis, receives data from lidi-send and stores it on disk",
    )
    parser.add_argument(
        "data_directory",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--listen-address",
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "--listen-port",
        type=int,
        default=6001,
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=logging.getLevelName(logging.INFO),
        choices=logging.getLevelNamesMapping().keys(),
    )
    parser.add_argument(
        "--socket-path",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/lidir.sock"),
    )

    args = parser.parse_args()

    DATA_DIRECTORY: pathlib.Path = args.data_directory
    SOCKET_PATH: pathlib.Path = args.socket_path

    logging.basicConfig(
        level=logging.getLevelNamesMapping()[args.log_level],
    )
    asyncio.run(
        _receiver_server(
            args.listen_address,
            args.listen_port,
        )
    )
