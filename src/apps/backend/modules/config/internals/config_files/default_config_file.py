from typing import cast

from modules.config.internals.config_utils import ConfigUtil
from modules.config.internals.types import Config


class DefaultConfig:

    FILENAME: str = "default.yml"

    @staticmethod
    def load() -> Config:
        default_config_dict = ConfigUtil.read_yml_from_config_dir(DefaultConfig.FILENAME)
        return cast(Config, default_config_dict)
