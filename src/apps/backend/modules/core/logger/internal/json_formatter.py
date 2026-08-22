import json
import logging
import os
from datetime import datetime, timezone
from logging import Formatter, LogRecord

from modules.core.config.config_service import ConfigService

TRACE_CORRELATION_ATTRIBUTES = ("dd.trace_id", "dd.span_id", "trace_id", "span_id")


class JsonFormatter(Formatter):
    def __init__(self) -> None:
        Formatter.__init__(self)
        self.service = ConfigService[str].get_value(key="logger.service")
        self.environment = os.environ.get("APP_ENV", "unknown")

    def format(self, record: LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "message": record.getMessage(),
            "status": self.__status_for(record),
            "level": record.levelname,
            "logger": record.name,
            "service": self.service,
            "environment": self.environment,
        }
        payload.update(self.__trace_correlation(record))

        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)

    def __status_for(self, record: LogRecord) -> str:
        if record.levelno <= logging.INFO:
            return "info"
        if record.levelno <= logging.WARNING:
            return "warn"
        return "error"

    def __trace_correlation(self, record: LogRecord) -> dict[str, object]:
        present = {}
        for attribute in TRACE_CORRELATION_ATTRIBUTES:
            value = getattr(record, attribute, None)
            if value is not None:
                present[attribute] = value
        return present
