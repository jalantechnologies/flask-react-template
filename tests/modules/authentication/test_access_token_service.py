from modules.account.account_service import AccountService
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import (
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams, OTPBasedAuthAccessTokenRequestParams
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken


class TestAuthenticationService(BaseTestAccessToken):
    def test_get_access_token_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)

        assert access_token.account_id == account.id
        assert access_token.token
        assert access_token.expires_at

    def test_verify_access_token_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)

        verified_access_token = AuthenticationService.verify_access_token(token=access_token.token)

        assert verified_access_token.account_id == account.id

    def test_get_access_token_by_phone_number(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number))
        )
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id
        )

        access_token = AuthenticationService.create_access_token_by_phone_number(
            params=OTPBasedAuthAccessTokenRequestParams(
                otp_code=otp.otp_code, phone_number=PhoneNumber(**phone_number)
            ),
            account=account,
        )

        assert access_token.account_id == account.id
        assert access_token.token
        assert access_token.expires_at

    def test_verify_access_token_by_phone_number(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number))
        )
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id
        )

        access_token = AuthenticationService.create_access_token_by_phone_number(
            params=OTPBasedAuthAccessTokenRequestParams(
                phone_number=PhoneNumber(**phone_number), otp_code=otp.otp_code
            ),
            account=account,
        )

        verified_access_token = AuthenticationService.verify_access_token(token=access_token.token)

        assert verified_access_token.account_id == account.id
