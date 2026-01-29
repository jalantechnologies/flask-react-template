import os
from typing import List

from modules.config.config_service import ConfigService
from modules.config.errors import MissingKeyError
from modules.config.types import ErrorCode
from tests.modules.config.base_test_config import BaseTestConfig


class TestConfig(BaseTestConfig):
    def test_db_config_is_loaded(self) -> None:
        uri = ConfigService[str].get_value(key="mongodb.uri")
        assert uri.split(":")[0] == "mongodb"
        assert uri.split("/")[-1] == "flask-react-template-test"

    def test_logger_config_is_loaded(self) -> None:
        loggers = ConfigService[List[str]].get_value(key="logger.transports")
        assert type(loggers) == list
        assert "console" in loggers

    def test_datadog_config_is_loaded(self) -> None:
        try:
            ConfigService[str].get_value(key="datadog.api_key")
        except MissingKeyError as exc:
            assert exc.code == ErrorCode.MISSING_KEY

        populated_env = os.environ.get("APP_ENV")
        assert populated_env == "testing"

    def test_app_env_values_are_valid(self) -> None:
        valid_app_env_values = {"development", "testing", "preview", "production"}
        populated_env = os.environ.get("APP_ENV")
        assert populated_env in valid_app_env_values

    def test_web_app_host_has_protocol(self) -> None:
        web_app_host = ConfigService[str].get_value(key="web_app_host")
        assert web_app_host.startswith("http://") or web_app_host.startswith("https://")
