import unittest
from typing import Callable


class BaseTestConfig(unittest.TestCase):
    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")
