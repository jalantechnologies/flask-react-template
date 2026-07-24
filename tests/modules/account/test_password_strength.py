from unittest.mock import MagicMock, patch

from modules.account.account_service import AccountService
from modules.account.errors import AccountPasswordTooWeakError
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import AccountErrorCode, CreateAccountByUsernameAndPasswordParams
from tests.conftest import TEST_ACTOR
from tests.modules.account.base_test_account import BaseTestAccount

WEAK_PASSWORD = "password"
STRONG_PASSWORD = "correct horse battery staple 12"


class TestPasswordStrength(BaseTestAccount):
    @patch("modules.account.internal.account_util.ConfigService.get_value", return_value=3)
    def test_create_account_rejects_a_weak_password_with_helpful_feedback(self, _mock_min_score: MagicMock) -> None:
        try:
            AccountService.create_account_by_username_and_password(
                params=CreateAccountByUsernameAndPasswordParams(
                    first_name="first_name", last_name="last_name", password=WEAK_PASSWORD, username="weak@example.com"
                ),
                actor=TEST_ACTOR,
            )
            assert False, "Expected AccountPasswordTooWeakError to be raised"
        except AccountPasswordTooWeakError as exc:
            assert exc.code == AccountErrorCode.PASSWORD_TOO_WEAK
            assert exc.http_code == 400
            assert "too weak" in exc.message.lower()
            assert len(exc.message) > len("This password is too weak.")

    @patch("modules.account.internal.account_util.ConfigService.get_value", return_value=3)
    def test_create_account_accepts_a_strong_password(self, _mock_min_score: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password=STRONG_PASSWORD, username="strong@example.com"
            ),
            actor=TEST_ACTOR,
        )

        assert account.username == "strong@example.com"

    @patch("modules.account.internal.account_util.ConfigService.get_value", return_value=3)
    def test_update_password_rejects_a_weak_password(self, _mock_min_score: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password=STRONG_PASSWORD, username="reset@example.com"
            ),
            actor=TEST_ACTOR,
        )

        try:
            AccountWriter.update_password_by_account_id(account_id=account.id, password=WEAK_PASSWORD, actor=TEST_ACTOR)
            assert False, "Expected AccountPasswordTooWeakError to be raised"
        except AccountPasswordTooWeakError as exc:
            assert exc.code == AccountErrorCode.PASSWORD_TOO_WEAK

    @patch("modules.account.internal.account_util.ConfigService.get_value", return_value=3)
    def test_create_account_rejects_an_oversized_password_before_scoring(self, mock_min_score: MagicMock) -> None:
        oversized_password = "a" * 129

        try:
            AccountService.create_account_by_username_and_password(
                params=CreateAccountByUsernameAndPasswordParams(
                    first_name="first_name",
                    last_name="last_name",
                    password=oversized_password,
                    username="oversized@example.com",
                ),
                actor=TEST_ACTOR,
            )
            assert False, "Expected AccountPasswordTooWeakError to be raised"
        except AccountPasswordTooWeakError as exc:
            assert exc.code == AccountErrorCode.PASSWORD_TOO_WEAK
            assert "at most 128 characters" in exc.message
            mock_min_score.assert_not_called()

    @patch("modules.account.internal.account_util.ConfigService.get_value", return_value=3)
    def test_update_password_accepts_a_strong_password(self, _mock_min_score: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password=STRONG_PASSWORD, username="reset2@example.com"
            ),
            actor=TEST_ACTOR,
        )

        updated = AccountWriter.update_password_by_account_id(
            account_id=account.id, password="another strong pass 4291", actor=TEST_ACTOR
        )

        assert updated.id == account.id
