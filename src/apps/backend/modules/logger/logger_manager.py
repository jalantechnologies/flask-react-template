from modules.logger.internal.loggers import Loggers


class LoggerManager:
    @staticmethod
    def mount_logger() -> None:
        Loggers.initialize_loggers()
