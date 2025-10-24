from typing import Union

from modules.config.config_service import ConfigService
from modules.logger.internal.console_logger import ConsoleLogger
from modules.logger.internal.datadog_logger import DatadogLogger
from modules.logger.internal.types import LoggerTransports


class Loggers:
    _LOGGERS: list[Union[ConsoleLogger, DatadogLogger]] = []

    @staticmethod
    def initialize_loggers() -> None:
        logger_transports = ConfigService[list[str]].get_value(key="logger.transports")
        for logger_transport in logger_transports:
            if logger_transport == LoggerTransports.CONSOLE:
                Loggers._LOGGERS.append(Loggers.__get_console_logger())

            if logger_transport == LoggerTransports.DATADOG:
                Loggers._LOGGERS.append(Loggers.__get_datadog_logger())

    @staticmethod
    def info(*, message: str) -> None:
        [logger.info(message=message) for logger in Loggers._LOGGERS]

    @staticmethod
    def debug(*, message: str) -> None:
        [logger.debug(message=message) for logger in Loggers._LOGGERS]

    @staticmethod
    def error(*, message: str) -> None:
        [logger.error(message=message) for logger in Loggers._LOGGERS]

    @staticmethod
    def warn(*, message: str) -> None:
        [logger.warn(message=message) for logger in Loggers._LOGGERS]

    @staticmethod
    def critical(*, message: str) -> None:
        [logger.critical(message=message) for logger in Loggers._LOGGERS]

    @staticmethod
    def __get_console_logger() -> ConsoleLogger:
        return ConsoleLogger()

    @staticmethod
    def __get_datadog_logger() -> DatadogLogger:
        return DatadogLogger()
