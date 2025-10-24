import logging

from modules.config.config_service import ConfigService
from modules.logger.internal.logger_enum import Levels


class LogLevel:
    @staticmethod
    def get_level() -> int:
        ddconfig_level = ConfigService[str].get_value(key="datadog.log_level")
        datadog_level = ddconfig_level.lower()
        for level in Levels:
            if datadog_level.lower() == level.name:
                return level.value
        return logging.DEBUG
