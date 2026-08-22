import logging
import sys

from modules.logger.internal.base_logger import BaseLogger
from modules.logger.internal.json_formatter import JsonFormatter
from modules.logger.internal.log_level import LogLevel


class ConsoleLogger(BaseLogger):
    def __init__(self) -> None:
        configured_level = LogLevel.get_level()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(configured_level)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(configured_level)
        console_handler.setFormatter(JsonFormatter())

        self._attach_handler(self.logger, console_handler)

    def critical(self, *, message: str) -> None:
        self.logger.critical(msg=message)

    def debug(self, *, message: str) -> None:
        self.logger.debug(msg=message)

    def error(self, *, message: str) -> None:
        self.logger.error(msg=message)

    def info(self, *, message: str) -> None:
        self.logger.info(msg=message)

    def warn(self, *, message: str) -> None:
        self.logger.warning(msg=message)
