from abc import ABC, abstractmethod


class BaseLogger(ABC):
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
