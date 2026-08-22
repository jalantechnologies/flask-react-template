import logging

from modules.core.config.config_service import ConfigService
from modules.core.logger.internal.logger_enum import Levels


class LogLevel:
    @staticmethod
    def get_level() -> int:
        configured_level = ConfigService[str].get_value(key="logger.level").lower()
        for level in Levels:
            if configured_level == level.name:
                return level.value
        return logging.INFO
