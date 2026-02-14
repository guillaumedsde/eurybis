import argparse
import asyncio
import logging
import pathlib
import uuid

LOGGER = logging.getLogger(__name__)


async def handle_file(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    LOGGER.info(f"Received from {addr!r}")
    filepath = DATA_DIRECTORY / str(uuid.uuid4())
    with filepath.open("wb") as dest_file:
        while chunk := await reader.read(CHUNK_SIZE):
            # Offload file write to thread to avoid blocking
            await asyncio.to_thread(dest_file.write, chunk)

    LOGGER.info("Close the connection")
    writer.close()
    await writer.wait_closed()


async def receiver_server(address: str, port: int):
    server = await asyncio.start_server(handle_file, address, port)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    LOGGER.info(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


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
        default="localhost",
    )
    parser.add_argument(
        "--listen-port",
        type=int,
        default=6000,
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=logging.getLevelName(logging.INFO),
        choices=logging.getLevelNamesMapping().keys(),
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=2 * 1024 ^ 2,  # 2MB,
    )
    args = parser.parse_args()

    DATA_DIRECTORY: pathlib.Path = args.data_directory
    CHUNK_SIZE: int = args.chunk_size

    logging.basicConfig(
        level=logging.getLevelNamesMapping()[args.log_level],
    )
    asyncio.run(
        receiver_server(
            args.listen_address,
            args.listen_port,
        )
    )
