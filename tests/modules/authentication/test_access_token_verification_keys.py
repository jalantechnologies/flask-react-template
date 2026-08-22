import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Callable, Iterator, List, Optional

import jwt

from modules.account.types import Account
from modules.authentication.errors import AccessTokenExpiredError, AccessTokenInvalidError
from modules.authentication.internal.access_token.access_token_util import AccessTokenUtil
from modules.config.config_service import ConfigService
from modules.config.internal.config_manager import ConfigManager

ACCOUNT_ID = "665a1f2b3c4d5e6f70819243"
OLD_SIGNING_KEY = "old-high-entropy-signing-key"
NEW_SIGNING_KEY = "new-high-entropy-signing-key"
UNKNOWN_SIGNING_KEY = "unknown-high-entropy-signing-key"


@contextmanager
def _keys(signing_key: str, verification_keys: Optional[List[str]] = None) -> Iterator[None]:
    previous_manager = ConfigService.config_manager

    manager = ConfigManager()
    accounts = manager.config_store["accounts"]
    assert isinstance(accounts, dict)
    accounts["token_signing_key"] = signing_key
    accounts["token_verification_keys"] = list(verification_keys or [])

    ConfigService.config_manager = manager
    try:
        yield
    finally:
        ConfigService.config_manager = previous_manager


def _account() -> Account:
    return Account(
        id=ACCOUNT_ID,
        first_name="first_name",
        last_name="last_name",
        hashed_password="hashed_password",
        phone_number=None,
        username="username",
    )


def _token(signing_key: str, expires_in: timedelta) -> str:
    payload = {"account_id": ACCOUNT_ID, "exp": (datetime.now() + expires_in).timestamp()}
    return jwt.encode(payload, signing_key, algorithm="HS256")


class TestAccessTokenVerificationKeys(unittest.TestCase):
    def setup_method(self, method: Callable[..., object]) -> None:
        print(f"Executing:: {method.__name__}")

    def teardown_method(self, method: Callable[..., object]) -> None:
        print(f"Executed:: {method.__name__}")

    def test_token_from_rotated_out_key_still_verifies(self) -> None:
        with _keys(signing_key=OLD_SIGNING_KEY):
            token = AccessTokenUtil.generate_access_token(account=_account()).token

        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=[OLD_SIGNING_KEY]):
            payload = AccessTokenUtil.verify_access_token(token=token)

        assert payload.account_id == ACCOUNT_ID

    def test_token_from_current_signing_key_verifies(self) -> None:
        token = _token(NEW_SIGNING_KEY, timedelta(days=1))

        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=[OLD_SIGNING_KEY]):
            payload = AccessTokenUtil.verify_access_token(token=token)

        assert payload.account_id == ACCOUNT_ID

    def test_expired_token_on_signing_key_reports_expired(self) -> None:
        token = _token(NEW_SIGNING_KEY, timedelta(days=-1))

        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=[OLD_SIGNING_KEY]):
            with self.assertRaises(AccessTokenExpiredError):
                AccessTokenUtil.verify_access_token(token=token)

    def test_expired_token_on_verification_key_reports_expired(self) -> None:
        token = _token(OLD_SIGNING_KEY, timedelta(days=-1))

        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=[OLD_SIGNING_KEY]):
            with self.assertRaises(AccessTokenExpiredError):
                AccessTokenUtil.verify_access_token(token=token)

    def test_token_from_unknown_key_is_rejected(self) -> None:
        token = _token(UNKNOWN_SIGNING_KEY, timedelta(days=1))

        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=[OLD_SIGNING_KEY]):
            with self.assertRaises(AccessTokenInvalidError):
                AccessTokenUtil.verify_access_token(token=token)

    def test_malformed_token_is_rejected(self) -> None:
        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=[OLD_SIGNING_KEY]):
            with self.assertRaises(AccessTokenInvalidError):
                AccessTokenUtil.verify_access_token(token="not-a-jwt")

    def test_blank_verification_keys_are_discarded(self) -> None:
        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=["   ", ""]):
            assert AccessTokenUtil._get_accepted_verification_keys() == [NEW_SIGNING_KEY]

    def test_padded_verification_key_is_trimmed_and_accepted(self) -> None:
        token = _token(OLD_SIGNING_KEY, timedelta(days=1))

        with _keys(signing_key=NEW_SIGNING_KEY, verification_keys=[f"  {OLD_SIGNING_KEY}  "]):
            payload = AccessTokenUtil.verify_access_token(token=token)

        assert payload.account_id == ACCOUNT_ID

    def test_no_verification_keys_accepts_only_signing_key(self) -> None:
        token = _token(OLD_SIGNING_KEY, timedelta(days=1))

        with _keys(signing_key=NEW_SIGNING_KEY):
            with self.assertRaises(AccessTokenInvalidError):
                AccessTokenUtil.verify_access_token(token=token)
