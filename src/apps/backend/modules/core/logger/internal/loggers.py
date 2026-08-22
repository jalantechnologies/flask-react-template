from modules.core.config.config_service import ConfigService
from modules.core.logger.internal.console_logger import ConsoleLogger
from modules.core.logger.internal.types import RETIRED_LOGGER_TRANSPORTS, LoggerTransports


class Loggers:
    _LOGGERS: list[ConsoleLogger] = []

    @staticmethod
    def initialize_loggers() -> None:
        if Loggers._LOGGERS:
            return

        Loggers._LOGGERS.append(ConsoleLogger())

        for logger_transport in Loggers.__configured_transports():
            if logger_transport in RETIRED_LOGGER_TRANSPORTS:
                Loggers.warn(
                    message=(
                        f"logger.transports lists '{logger_transport}', which no longer exists. "
                        f"Logs are written to stdout as JSON and collected by the platform. "
                        f"Set logger.transports to ['{LoggerTransports.CONSOLE}']."
                    )
                )
            elif logger_transport != LoggerTransports.CONSOLE:
                Loggers.warn(message=f"logger.transports lists unknown transport '{logger_transport}'; ignoring it.")

    @staticmethod
    def info(*, message: str) -> None:
        for logger in Loggers._LOGGERS:
            logger.info(message=message)

    @staticmethod
    def debug(*, message: str) -> None:
        for logger in Loggers._LOGGERS:
            logger.debug(message=message)

    @staticmethod
    def error(*, message: str) -> None:
        for logger in Loggers._LOGGERS:
            logger.error(message=message)

    @staticmethod
    def warn(*, message: str) -> None:
        for logger in Loggers._LOGGERS:
            logger.warn(message=message)

    @staticmethod
    def critical(*, message: str) -> None:
        for logger in Loggers._LOGGERS:
            logger.critical(message=message)

    @staticmethod
    def __configured_transports() -> list[str]:
        return ConfigService[list[str]].get_value(key="logger.transports", default=[LoggerTransports.CONSOLE])
