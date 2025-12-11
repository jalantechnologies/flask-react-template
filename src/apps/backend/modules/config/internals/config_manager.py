from typing import Optional, cast

from modules.config.internals.config_files.app_env_config_file import AppEnvConfig
from modules.config.internals.config_files.custom_env_config_file import CustomEnvConfig
from modules.config.internals.config_files.default_config_file import DefaultConfig
from modules.config.internals.config_utils import ConfigUtil
from modules.config.internals.types import Config
from modules.config.types import ConfigType


class ConfigManager:

    CONFIG_KEY_SEPARATOR: str = "."

    def __init__(self) -> None:
        default_content = DefaultConfig.load()
        app_env_content = AppEnvConfig.load()
        os_env_content = CustomEnvConfig.load()

        merged_content = ConfigUtil.deep_merge(default_content, app_env_content, os_env_content)

        self.config_store: Config = merged_content

    def get(self, key: str, default: Optional[ConfigType] = None) -> Optional[ConfigType]:
        value = self._traverse_config(key)
        return value if value is not None else default

    def has(self, key: str) -> bool:
        return self._traverse_config(key) is not None

    def _traverse_config(self, key: str) -> Optional[ConfigType]:
        values = self.config_store
        for k in key.split(self.CONFIG_KEY_SEPARATOR):
            if not isinstance(values, dict) or k not in values:
                return None

            next_values = values[k]

            if not isinstance(next_values, dict):
                return cast(ConfigType, next_values)

            values = next_values

        return cast(ConfigType, values)
