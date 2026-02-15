import logging

from eurybis.config import (
    COMMAND_TO_DATACLASS,
    DestinationEurybisConfiguration,
    OriginEurybisConfiguration,
    root_parser,
)
from eurybis.destination import destination_server
from eurybis.origin import origin_server

CMD_TO_CALLABLE = {
    "destination": destination_server,
    "origin": origin_server,
}

if __name__ == "__main__":
    args = root_parser.parse_args()
    config: OriginEurybisConfiguration | DestinationEurybisConfiguration = (
        COMMAND_TO_DATACLASS[args.command](**vars(args))
    )

    logging.basicConfig(
        level=logging.getLevelNamesMapping()[config.log_level],
    )

    CMD_TO_CALLABLE[args.command](config)
