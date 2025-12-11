import os
from pathlib import Path
from typing import Any, cast

import yaml

from modules.config.internals.types import Config


class ConfigUtil:
    DIR_LEVELS_FROM_BASE_DIR_TO_CONFIG_UTILS: int = 6
    CURRENT_FILE: str = __file__

    @staticmethod
    def deep_merge(*configs: Config) -> Config:
        merged_config: Config = {}

        for config in configs:
            for key, value in config.items():
                if isinstance(value, dict) and key in merged_config and isinstance(merged_config[key], dict):
                    merged_config[key] = ConfigUtil.deep_merge(cast(Config, merged_config[key]), value)
                else:
                    merged_config[key] = value

        return merged_config

    @staticmethod
    def read_yml_from_config_dir(filename: str) -> dict[str, Any]:
        config_path = ConfigUtil._get_base_config_directory(ConfigUtil.CURRENT_FILE)
        file_path = os.path.join(config_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = yaml.safe_load(file) or {}
        except FileNotFoundError:
            # Raised when filename is not found in config dir
            raise FileNotFoundError(f"Config file '{filename}' not found in {config_path}")

        return content

    @staticmethod
    def _get_base_config_directory(current_file: str) -> Path:
        base_directory = Path(current_file).resolve().parents[ConfigUtil.DIR_LEVELS_FROM_BASE_DIR_TO_CONFIG_UTILS]
        config_directory = os.path.join(base_directory, "config")

        config_path = Path(config_directory)  # Convert back to Path for consistency

        if not config_path.exists() or not config_path.is_dir():
            raise FileNotFoundError(f"Config directory does not exist: {config_directory}")

        return config_path
