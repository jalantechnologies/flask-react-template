import json
import logging
import os

from modules.config.config_service import ConfigService
from modules.logger.internal.json_formatter import JsonFormatter
from tests.modules.logger.base_test_logger import BaseTestLogger


class TestJsonFormatter(BaseTestLogger):
    def test_every_line_is_one_json_object(self) -> None:
        logger, stream = self.build_logger(logging.DEBUG)

        logger.debug("first")
        logger.info("second")
        logger.warning("third")
        logger.error("fourth")

        raw_lines = [line for line in stream.getvalue().splitlines() if line]
        assert len(raw_lines) == 4
        for raw_line in raw_lines:
            assert isinstance(json.loads(raw_line), dict)

    def test_line_carries_timestamp_message_status_service_and_environment(self) -> None:
        logger, stream = self.build_logger(logging.INFO)

        logger.info("account created")

        line = self.emitted_lines(stream)[0]
        assert line["message"] == "account created"
        assert line["status"] == "info"
        assert line["level"] == "INFO"
        assert line["service"] == ConfigService[str].get_value(key="logger.service")
        assert line["environment"] == os.environ.get("APP_ENV")
        assert isinstance(line["timestamp"], str)

    def test_status_maps_level_to_datadog_severity(self) -> None:
        logger, stream = self.build_logger(logging.DEBUG)

        logger.debug("a")
        logger.info("b")
        logger.warning("c")
        logger.error("d")
        logger.critical("e")

        assert [line["status"] for line in self.emitted_lines(stream)] == ["info", "info", "warn", "error", "error"]

    def test_message_interpolation_happens_before_serialization(self) -> None:
        logger, stream = self.build_logger(logging.INFO)

        logger.info("processed %s items", 12)

        assert self.emitted_lines(stream)[0]["message"] == "processed 12 items"

    def test_trace_correlation_ids_are_included_when_present(self) -> None:
        logger, stream = self.build_logger(logging.INFO)

        logger.info("traced", extra={"dd.trace_id": "111", "dd.span_id": "222"})

        line = self.emitted_lines(stream)[0]
        assert line["dd.trace_id"] == "111"
        assert line["dd.span_id"] == "222"

    def test_trace_correlation_ids_are_absent_when_not_on_the_record(self) -> None:
        logger, stream = self.build_logger(logging.INFO)

        logger.info("untraced")

        line = self.emitted_lines(stream)[0]
        assert "dd.trace_id" not in line
        assert "dd.span_id" not in line

    def test_exception_is_serialized_into_the_same_object(self) -> None:
        logger, stream = self.build_logger(logging.INFO)

        try:
            raise ValueError("boom")
        except ValueError:
            logger.exception("failed to process")

        lines = self.emitted_lines(stream)
        assert len(lines) == 1
        assert "ValueError: boom" in str(lines[0]["error"])

    def test_multiline_message_stays_a_single_json_line(self) -> None:
        logger, stream = self.build_logger(logging.INFO)

        logger.info("line one\nline two")

        raw_lines = [line for line in stream.getvalue().splitlines() if line]
        assert len(raw_lines) == 1
        assert json.loads(raw_lines[0])["message"] == "line one\nline two"

    def test_service_and_environment_are_resolved_once_at_construction(self) -> None:
        formatter = JsonFormatter()

        first = json.loads(formatter.format(self.__record("one")))
        second = json.loads(formatter.format(self.__record("two")))

        assert first["service"] == second["service"] == formatter.service
        assert first["environment"] == second["environment"] == formatter.environment

    def __record(self, message: str) -> logging.LogRecord:
        return logging.LogRecord(
            name="test", level=logging.INFO, pathname=__file__, lineno=1, msg=message, args=(), exc_info=None
        )
