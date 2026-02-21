import argparse
import os
import pathlib
from dataclasses import dataclass

from eurybis.config.main import BaseEurybisConfiguration


@dataclass
class DestinationEurybisConfiguration(BaseEurybisConfiguration):
    data_directory: pathlib.Path
    lidir_socket_path: pathlib.Path
    lidir_listen_host: str
    lidir_listen_port: int


destination_parser = argparse.ArgumentParser(add_help=False)

destination_parser.add_argument(
    "data_directory",
    type=pathlib.Path,
)

destination_parser.add_argument(
    "--lidir-socket-path",
    type=pathlib.Path,
    default=pathlib.Path(os.environ.get("XDG_RUNTIME_DIR", "/run")) / "lidir.sock",
)

destination_parser.add_argument(
    "--lidir-listen-host",
    type=str,
    default="127.0.0.1",
)

destination_parser.add_argument(
    "--lidir-listen-port",
    type=int,
    default=6000,
)
