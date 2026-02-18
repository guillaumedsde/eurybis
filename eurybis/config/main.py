import argparse
import logging
import pathlib
from dataclasses import dataclass


@dataclass
class BaseEurybisConfiguration:
    command: str
    log_level: str
    pipe_size: int


root_parser = argparse.ArgumentParser(
    prog="Eurybis",
    description="HTTP API for sending data through a unidirectional network link",
)

root_parser.add_argument(
    "--log-level",
    type=str,
    default=logging.getLevelName(logging.INFO),
    choices=logging.getLevelNamesMapping().keys(),
)

root_parser.add_argument(
    "--pipe-size",
    type=int,
    default=int(pathlib.Path("/proc/sys/fs/pipe-max-size").read_text()),
)
