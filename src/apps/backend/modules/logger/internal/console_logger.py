import logging

from modules.logger.internal.base_logger import BaseLogger


class ConsoleLogger(BaseLogger):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create a console handler and set the level to INFO
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

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
