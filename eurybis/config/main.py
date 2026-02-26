import argparse
import logging
from dataclasses import dataclass


@dataclass
class BaseEurybisConfiguration:
    command: str
    log_level: str
    lidi_max_clients: int
    lidi_udp_mtu: int
    lidi_udp_batch_size: int


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

root_parser.add_argument("--lidi-max-clients", type=int, default=200)

root_parser.add_argument("--lidi-udp-mtu", type=int, default=9000)
root_parser.add_argument("--lidi-udp-batch-size", type=int, default=128)
