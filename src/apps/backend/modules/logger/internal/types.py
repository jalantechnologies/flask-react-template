from dataclasses import dataclass


@dataclass(frozen=True)
class LoggerTransports:
    CONSOLE: str = "console"
    DATADOG: str = "datadog"
