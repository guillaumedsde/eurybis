from eurybis.config.destination import (
    DestinationEurybisConfiguration,
    destination_parser,
)
from eurybis.config.main import root_parser
from eurybis.config.origin import OriginEurybisConfiguration, origin_parser

subparsers = root_parser.add_subparsers(dest="command", required=True)
subparsers.add_parser("origin", parents=[origin_parser])
subparsers.add_parser("destination", parents=[destination_parser])

COMMAND_TO_DATACLASS = {
    "origin": OriginEurybisConfiguration,
    "destination": DestinationEurybisConfiguration,
}

__all__ = (
    "root_parser",
    "OriginEurybisConfiguration",
    "DestinationEurybisConfiguration",
    "COMMAND_TO_DATACLASS",
)
