import io
import json
import logging
import unittest
from typing import Callable

from modules.core.logger.internal.json_formatter import JsonFormatter


class BaseTestLogger(unittest.TestCase):
    def setup_method(self, method: Callable[..., object]) -> None:
        print(f"Executing:: {method.__name__}")

    def teardown_method(self, method: Callable[..., object]) -> None:
        print(f"Executed:: {method.__name__}")

    def build_logger(self, level: int) -> tuple[logging.Logger, io.StringIO]:
        stream = io.StringIO()
        logger = logging.getLogger(f"test.{self.id()}")
        logger.handlers.clear()
        logger.propagate = False
        logger.setLevel(level)

        handler = logging.StreamHandler(stream)
        handler.setLevel(level)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

        return logger, stream

    def emitted_lines(self, stream: io.StringIO) -> list[dict[str, object]]:
        return [json.loads(line) for line in stream.getvalue().splitlines() if line]
