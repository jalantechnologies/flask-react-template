import unittest
from typing import Callable

from modules.logger.logger_manager import LoggerManager


class BaseTestApplication(unittest.TestCase):
    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")
        LoggerManager.mount_logger()

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")
