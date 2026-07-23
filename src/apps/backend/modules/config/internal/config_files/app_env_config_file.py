import os
from typing import cast

from modules.config.internal.config_utils import ConfigUtil
from modules.config.internal.types import Config


class AppEnvConfig:

    FILENAME: str

    @staticmethod
    def load() -> Config:
        app_env = os.environ.get("APP_ENV", "development")
        AppEnvConfig.FILENAME = f"{app_env}.yml"
        app_env_dict = ConfigUtil.read_yml_from_config_dir(AppEnvConfig.FILENAME)
        return cast(Config, app_env_dict)
