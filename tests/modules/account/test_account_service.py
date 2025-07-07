from unittest.mock import patch

from server import app

from modules.account.account_service import AccountService
from modules.account.errors import AccountNotFoundError
from modules.account.types import (
    AccountErrorCode,
    AccountSearchByIdParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.types import AccessTokenPayload
from tests.modules.account.base_test_account import BaseTestAccount


class TestAccountService(BaseTestAccount):
    def test_create_account_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                password="password", username="username", first_name="first_name", last_name="last_name"
            )
        )

        assert account.username == "username"
        assert account.first_name == "first_name"
        assert account.last_name == "last_name"

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_get_account_by_id(self, mock_verify_access_token) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        mock_verify_access_token.return_value = AccessTokenPayload(account_id=account.id)

        with app.test_request_context():
            get_account_by_id = AccountService.get_account_by_id(params=AccountSearchByIdParams(id=account.id))

        assert get_account_by_id.username == account.username
        assert get_account_by_id.first_name == account.first_name
        assert get_account_by_id.last_name == account.last_name

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_throw_exception_when_usernot_exist(self, mock_verify_access_token) -> None:
        try:
            mock_verify_access_token.return_value = AccessTokenPayload(account_id="5f7b1b7b4f3b9b1b3f3b9b1b")
            with app.test_request_context():
                AccountService.get_account_by_id(params=AccountSearchByIdParams(id="5f7b1b7b4f3b9b1b3f3b9b1b"))
        except AccountNotFoundError as exc:
            assert exc.code == AccountErrorCode.NOT_FOUND

    def test_get_or_create_account_by_phone_number(self) -> None:
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(
                phone_number=PhoneNumber(**{"country_code": "+91", "phone_number": "9999999999"})
            )
        )

        assert account.phone_number == PhoneNumber(country_code="+91", phone_number="9999999999")

    def test_throw_exception_when_phone_number_not_exist(self) -> None:
        phone_number = PhoneNumber(**{"country_code": "+91", "phone_number": "9999999999"})
        try:
            AccountService.get_account_by_phone_number(phone_number=phone_number)
        except AccountNotFoundError as exc:
            assert exc.code == AccountErrorCode.NOT_FOUND
            assert (
                exc.message
                == f"We could not find an account phone number: {phone_number}. Please verify it or you can create a new account."
            )
