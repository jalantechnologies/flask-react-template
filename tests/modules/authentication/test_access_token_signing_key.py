import os
import unittest
from contextlib import contextmanager
from typing import Callable, Iterator, Optional

from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.errors import AccessTokenSigningKeyInsecureError
from modules.config.config_service import ConfigService
from modules.config.internal.config_manager import ConfigManager


@contextmanager
def _environment(app_env: str, signing_key: Optional[str]) -> Iterator[None]:
    previous_manager = ConfigService.config_manager
    previous_env = {name: os.environ.get(name) for name in ("APP_ENV", "ACCOUNTS_TOKEN_SIGNING_KEY")}

    os.environ["APP_ENV"] = app_env
    if signing_key is None:
        os.environ.pop("ACCOUNTS_TOKEN_SIGNING_KEY", None)
    else:
        os.environ["ACCOUNTS_TOKEN_SIGNING_KEY"] = signing_key

    ConfigService.config_manager = ConfigManager()
    try:
        yield
    finally:
        ConfigService.config_manager = previous_manager
        for name, value in previous_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


class TestAccessTokenSigningKey(unittest.TestCase):
    def setup_method(self, method: Callable[..., object]) -> None:
        print(f"Executing:: {method.__name__}")

    def teardown_method(self, method: Callable[..., object]) -> None:
        print(f"Executed:: {method.__name__}")

    def test_deployed_env_without_signing_key_refuses_boot(self) -> None:
        with _environment(app_env="production", signing_key=None):
            with self.assertRaises(AccessTokenSigningKeyInsecureError):
                AuthenticationService.validate_access_token_signing_key()

    def test_deployed_env_with_placeholder_key_refuses_boot(self) -> None:
        with _environment(app_env="production", signing_key="JWT_TOKEN"):
            with self.assertRaises(AccessTokenSigningKeyInsecureError):
                AuthenticationService.validate_access_token_signing_key()

    def test_deployed_env_with_proper_key_boots(self) -> None:
        with _environment(app_env="production", signing_key="a-high-entropy-production-signing-key"):
            AuthenticationService.validate_access_token_signing_key()

    def test_local_env_boots_with_bundled_dev_key(self) -> None:
        with _environment(app_env="testing", signing_key=None):
            AuthenticationService.validate_access_token_signing_key()
