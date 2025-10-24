from modules.logger.internal.loggers import Loggers


class Logger:
    @staticmethod
    def critical(*, message: str) -> None:
        Loggers.critical(message=message)

    @staticmethod
    def info(*, message: str) -> None:
        Loggers.info(message=message)

    @staticmethod
    def debug(*, message: str) -> None:
        Loggers.debug(message=message)

    @staticmethod
    def error(*, message: str) -> None:
        Loggers.error(message=message)

    @staticmethod
    def warn(*, message: str) -> None:
        Loggers.warn(message=message)
