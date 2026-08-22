import os
from typing import Callable

from modules.core.config.internal.config_files.custom_env_config_file import CustomEnvConfig
from modules.core.config.internal.config_utils import ConfigUtil
from modules.core.config.internal.types import Config
from tests.modules.core.base_test_config import BaseTestConfig


class TestCustomEnvConfig(BaseTestConfig):
    UNSET_ENV_VAR = "FLASK_REACT_TEMPLATE_TEST_UNSET_ENV_VAR"

    def setup_method(self, method: Callable[..., object]) -> None:
        super().setup_method(method)
        os.environ.pop(self.UNSET_ENV_VAR, None)

    def test_unset_name_mapping_omits_key(self) -> None:
        overrides = CustomEnvConfig._apply_environment_overrides({"feature": {"__name": self.UNSET_ENV_VAR}})
        assert "feature" not in overrides

    def test_unset_name_mapping_does_not_blank_base_value(self) -> None:
        base_layer: Config = {"feature": {"enabled": True}}
        override_layer = CustomEnvConfig._apply_environment_overrides({"feature": {"__name": self.UNSET_ENV_VAR}})

        merged = ConfigUtil.deep_merge(base_layer, override_layer)

        assert merged["feature"] == {"enabled": True}

    def test_set_name_mapping_overrides_base_value(self) -> None:
        os.environ[self.UNSET_ENV_VAR] = "from-env"
        try:
            overrides = CustomEnvConfig._apply_environment_overrides({"feature": {"__name": self.UNSET_ENV_VAR}})
        finally:
            os.environ.pop(self.UNSET_ENV_VAR, None)

        assert overrides["feature"] == "from-env"

    def test_list_format_splits_comma_separated_value(self) -> None:
        os.environ[self.UNSET_ENV_VAR] = "first, second ,third"
        try:
            overrides = CustomEnvConfig._apply_environment_overrides(
                {"keys": {"__name": self.UNSET_ENV_VAR, "__format": "list"}}
            )
        finally:
            os.environ.pop(self.UNSET_ENV_VAR, None)

        assert overrides["keys"] == ["first", "second", "third"]

    def test_list_format_drops_empty_entries(self) -> None:
        os.environ[self.UNSET_ENV_VAR] = " , only ,"
        try:
            overrides = CustomEnvConfig._apply_environment_overrides(
                {"keys": {"__name": self.UNSET_ENV_VAR, "__format": "list"}}
            )
        finally:
            os.environ.pop(self.UNSET_ENV_VAR, None)

        assert overrides["keys"] == ["only"]

    def test_unset_list_format_omits_key(self) -> None:
        overrides = CustomEnvConfig._apply_environment_overrides(
            {"keys": {"__name": self.UNSET_ENV_VAR, "__format": "list"}}
        )

        assert "keys" not in overrides

    def test_nested_dict_without_name_still_merges(self) -> None:
        os.environ[self.UNSET_ENV_VAR] = "child-value"
        try:
            overrides = CustomEnvConfig._apply_environment_overrides(
                {"parent": {"child": {"__name": self.UNSET_ENV_VAR}}}
            )
        finally:
            os.environ.pop(self.UNSET_ENV_VAR, None)

        assert overrides["parent"] == {"child": "child-value"}
