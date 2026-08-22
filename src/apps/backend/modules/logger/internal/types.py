from dataclasses import dataclass


@dataclass(frozen=True)
class LoggerTransports:
    CONSOLE: str = "console"


RETIRED_LOGGER_TRANSPORTS: frozenset[str] = frozenset({"datadog"})
