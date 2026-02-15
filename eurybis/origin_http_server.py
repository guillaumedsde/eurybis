import argparse
import logging
import pathlib
import subprocess
import sys

import uvicorn

import eurybis.api

LOGGER = logging.getLogger(__name__)


def _origin():
    SOCKET_PATH.unlink(missing_ok=True)
    LOGGER.info("Starting lidi")
    subprocess.Popen(
        (
            "diode-send",
            f"--from-unix={SOCKET_PATH}",
            "--to=127.0.0.1:6001",
        ),
        stderr=sys.stderr,
        stdout=sys.stdout,
    )
    uvicorn.run(
        eurybis.api.app,
        host="127.0.0.1",
        port=8080,
        log_level="info",
        http="httptools",
        loop="uvloop",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="eurybis-send",
        description="Receiver for Eurybis, receives data from lidi-send and stores it on disk",
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

    SOCKET_PATH: pathlib.Path = args.socket_path

    logging.basicConfig(
        level=logging.getLevelNamesMapping()[args.log_level],
    )

    _origin()
