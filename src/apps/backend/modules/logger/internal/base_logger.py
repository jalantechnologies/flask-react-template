import logging
from abc import ABC, abstractmethod


class BaseLogger(ABC):
    def _attach_handler(self, logger: logging.Logger, handler: logging.Handler) -> None:
        # Python loggers are process-global singletons keyed by name, so any logger setup that runs more
        # than once (for example once per test via mount_logger) would otherwise stack a duplicate handler
        # each time and multiply every log line. Attaching a given handler type at most once makes setup
        # idempotent by construction, so callers do not have to guard against repeated initialization.
        if any(isinstance(existing, type(handler)) for existing in logger.handlers):
            return
        logger.addHandler(handler)

    @abstractmethod
    def critical(self, *, message: str) -> None: ...

    @abstractmethod
    def debug(self, *, message: str) -> None: ...

    @abstractmethod
    def error(self, *, message: str) -> None: ...

    @abstractmethod
    def info(self, *, message: str) -> None: ...

    @abstractmethod
    def warn(self, *, message: str) -> None: ...
