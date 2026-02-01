import argparse
import asyncio
import logging

LOGGER = logging.getLogger(__name__)


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info("peername")

    LOGGER.info(f"Received {message!r} from {addr!r}")

    LOGGER.info(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    LOGGER.info("Close the connection")
    writer.close()
    await writer.wait_closed()


async def receiver_server(address: str, port: int):
    server = await asyncio.start_server(handle_echo, address, port)

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
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.getLevelNamesMapping()[args.log_level],
    )
    asyncio.run(receiver_server(args.listen_address, args.listen_port))
