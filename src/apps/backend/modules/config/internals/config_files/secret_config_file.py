from typing import Any, cast

from modules.config.internals.config_utils import ConfigUtil
from modules.config.internals.types import Config


class SecretConfig:

    FILENAME: str = "secret.yaml"

    @staticmethod
    def load() -> Config:
        try:
            secret_config = ConfigUtil.read_yml_from_config_dir(SecretConfig.FILENAME)
            secret_dict = SecretConfig._apply_file_path_overrides(secret_config)
            return cast(Config, secret_dict)
        except FileNotFoundError:
            # Return empty config if secret.yaml doesn't exist (backward compatibility)
            return cast(Config, {})

    @staticmethod
    def _apply_file_path_overrides(data: dict[str, Any]) -> dict[str, Any]:

        if not isinstance(data, dict):
            return data

        updated_data: dict[str, Any] = {}

        for key, value in data.items():
            if isinstance(value, dict):
                updated_data[key] = SecretConfig._apply_file_path_overrides(value)
            elif isinstance(value, str) and value.startswith("/"):
                file_value = ConfigUtil.read_value_from_file(value)
                if file_value is not None:
                    updated_data[key] = file_value

        return updated_data
