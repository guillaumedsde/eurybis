import argparse
import os
import pathlib
from dataclasses import dataclass

from eurybis.config.main import BaseEurybisConfiguration


@dataclass
class OriginEurybisConfiguration(BaseEurybisConfiguration):
    http_listen_host: str
    http_listen_port: int
    lidis_socket_path: pathlib.Path
    lidis_send_host: str
    lidis_send_port: int
    lidis_max_clients: int


origin_parser = argparse.ArgumentParser(add_help=False)

origin_parser.add_argument(
    "--http-listen-host",
    type=str,
    default="127.0.0.1",
)

origin_parser.add_argument(
    "--http-listen-port",
    type=int,
    default="8080",
)

origin_parser.add_argument(
    "--lidis-socket-path",
    type=pathlib.Path,
    default=pathlib.Path(os.environ.get("XDG_RUNTIME_DIR", "/run")) / "lidis.sock",
)

origin_parser.add_argument(
    "--lidis-send-host",
    type=str,
    default="127.0.0.1",
)

origin_parser.add_argument(
    "--lidis-send-port",
    type=int,
    default=6000,
)

origin_parser.add_argument(
    "--lidis-max-clients",
    type=int,
    default=100,
)
