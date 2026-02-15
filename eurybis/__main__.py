from eurybis.config import (
    COMMAND_TO_DATACLASS,
    DestinationEurybisConfiguration,
    OriginEurybisConfiguration,
    root_parser,
)

if __name__ == "__main__":
    args = root_parser.parse_args()
    print(args)
    config: OriginEurybisConfiguration | DestinationEurybisConfiguration = (
        COMMAND_TO_DATACLASS[args.command](**vars(args))
    )
    print(config)
