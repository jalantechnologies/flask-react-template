import unittest
from typing import Any, Callable


class BaseTestApplication(unittest.TestCase):
    def setup_method(self, method: Callable[..., Any]) -> None:
        print(f"Executing:: {method.__name__}")

    def teardown_method(self, method: Callable[..., Any]) -> None:
        print(f"Executed:: {method.__name__}")
