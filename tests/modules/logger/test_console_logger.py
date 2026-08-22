import io
import json
import logging
import socket
import sys
from contextlib import contextmanager
from typing import Iterator
from unittest.mock import patch

import pytest

from modules.config.config_service import ConfigService
from modules.logger.internal.console_logger import ConsoleLogger
from modules.logger.internal.log_level import LogLevel
from modules.logger.internal.loggers import Loggers
from tests.modules.logger.base_test_logger import BaseTestLogger


@pytest.fixture(autouse=True)
def restore_process_global_logger_state() -> Iterator[None]:
    registered_loggers = list(Loggers._LOGGERS)
    console_logger = logging.getLogger(ConsoleLogger.__module__)
    attached_handlers = list(console_logger.handlers)

    yield

    console_logger.handlers[:] = attached_handlers
    Loggers._LOGGERS[:] = registered_loggers


class TestConsoleLogger(BaseTestLogger):
    def test_configured_level_is_read_from_config(self) -> None:
        console_logger = self.__console_logger_at(logging.INFO)

        assert console_logger.logger.level == logging.INFO
        assert console_logger.logger.handlers[0].level == logging.INFO

    def test_info_level_stops_debug_lines(self) -> None:
        lines = self.__capture_lines(level=logging.INFO)

        assert [line["message"] for line in lines] == ["visible info", "visible warning"]

    def test_debug_level_emits_debug_lines(self) -> None:
        lines = self.__capture_lines(level=logging.DEBUG)

        assert [line["message"] for line in lines] == ["hidden debug", "visible info", "visible warning"]

    def test_unknown_configured_level_falls_back_to_info(self) -> None:
        with self.__configured_value(key="logger.level", value="not-a-level"):
            assert LogLevel.get_level() == logging.INFO

    def test_logging_opens_no_network_connection(self) -> None:
        console_logger = self.__console_logger_at(logging.DEBUG)
        stream = self.__redirect_to_string_io(console_logger)

        def refuse_connection(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("logging must not open a network connection")

        with patch.object(socket.socket, "connect", refuse_connection):
            with patch.object(socket.socket, "connect_ex", refuse_connection):
                for index in range(1000):
                    console_logger.info(message=f"line {index}")

        assert len(self.emitted_lines(stream)) == 1000

    def test_handler_writes_json_to_stdout(self) -> None:
        console_logger = self.__console_logger_at(logging.INFO)

        handler = console_logger.logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream is sys.stdout

        stream = self.__redirect_to_string_io(console_logger)
        console_logger.info(message="to stdout")

        assert json.loads(stream.getvalue().strip())["message"] == "to stdout"

    def test_console_is_the_only_registered_transport(self) -> None:
        registered = self.__initialize_with_transports(["console"])

        assert [type(logger) for logger in registered] == [ConsoleLogger]

    def test_stale_datadog_transport_still_registers_the_console_logger(self) -> None:
        registered = self.__initialize_with_transports(["console", "datadog"])

        assert [type(logger) for logger in registered] == [ConsoleLogger]

    def test_datadog_only_transport_does_not_leave_the_app_without_a_logger(self) -> None:
        registered = self.__initialize_with_transports(["datadog"])

        assert [type(logger) for logger in registered] == [ConsoleLogger]

    def test_stale_datadog_transport_warns_how_to_migrate(self) -> None:
        warnings: list[str] = []
        with patch.object(Loggers, "warn", lambda *, message: warnings.append(message)):
            self.__initialize_with_transports(["datadog"])

        assert len(warnings) == 1
        assert "datadog" in warnings[0]
        assert "stdout" in warnings[0]

    def test_unknown_transport_warns_and_is_ignored(self) -> None:
        warnings: list[str] = []
        with patch.object(Loggers, "warn", lambda *, message: warnings.append(message)):
            registered = self.__initialize_with_transports(["console", "logstash"])

        assert [type(logger) for logger in registered] == [ConsoleLogger]
        assert len(warnings) == 1
        assert "logstash" in warnings[0]

    def __initialize_with_transports(self, transports: list[str]) -> list[ConsoleLogger]:
        Loggers._LOGGERS.clear()
        logging.getLogger(ConsoleLogger.__module__).handlers.clear()

        with self.__configured_value(key="logger.transports", value=transports):
            Loggers.initialize_loggers()

        return list(Loggers._LOGGERS)

    @contextmanager
    def __configured_value(self, *, key: str, value: object) -> Iterator[None]:
        overridden_key = key
        config_manager = ConfigService.config_manager

        def get_value(key: str, default: object = None) -> object:
            if key == overridden_key:
                return value
            resolved = config_manager.get(key)
            return default if resolved is None else resolved

        with patch.object(ConfigService, "get_value", get_value):
            yield

    def __console_logger_at(self, level: int) -> ConsoleLogger:
        logging.getLogger(ConsoleLogger.__module__).handlers.clear()
        with patch.object(LogLevel, "get_level", return_value=level):
            return ConsoleLogger()

    def __redirect_to_string_io(self, console_logger: ConsoleLogger) -> io.StringIO:
        stream = io.StringIO()
        handler = console_logger.logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        handler.setStream(stream)
        return stream

    def __capture_lines(self, *, level: int) -> list[dict[str, object]]:
        console_logger = self.__console_logger_at(level)
        stream = self.__redirect_to_string_io(console_logger)

        console_logger.debug(message="hidden debug")
        console_logger.info(message="visible info")
        console_logger.warn(message="visible warning")

        return self.emitted_lines(stream)
