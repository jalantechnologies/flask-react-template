import json

from server import app

from modules.account.account_service import AccountService
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import (
    AccountErrorCode,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams, OTPErrorCode, VerifyOTPParams
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken

API_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestAccessTokenApi(BaseTestAccessToken):
    def test_get_access_token_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            response = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"username": account.username, "password": "password"})
            )
            assert response.status_code == 201
            assert response.json
            assert response.json.get("token")
            assert response.json.get("account_id") == account.id
            assert response.json.get("expires_at")

    def test_get_access_token_with_invalid_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            response = client.post(
                API_URL,
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "invalid_password"}),
            )
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccountErrorCode.INVALID_CREDENTIALS

    def test_get_access_token_with_invalid_username(self) -> None:
        with app.test_client() as client:
            response = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"username": "invalid_username", "password": "password"})
            )
            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_get_access_token_with_invalid_username_and_password(self) -> None:
        with app.test_client() as client:
            response = client.post(
                API_URL,
                headers=HEADERS,
                data=json.dumps({"username": "invalid_username", "password": "invalid_password"}),
            )
            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_get_access_token_by_phone_number_and_otp(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number))
        )

        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id
        )

        with app.test_client() as client:
            response = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"phone_number": phone_number, "otp_code": otp.otp_code})
            )
            assert response.status_code == 201
            assert response.json
            assert response.json.get("token")
            assert response.json.get("account_id") == account.id
            assert response.json.get("expires_at")

    def test_get_access_token_with_invalid_otp(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number))
        )

        with app.test_client() as client:
            response = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"phone_number": phone_number, "otp_code": "invalid_otp"})
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == OTPErrorCode.INCORRECT_OTP
        assert response.json.get("message") == "Please provide the correct OTP to login."

    def test_get_access_token_with_invalid_phone_number(self) -> None:
        with app.test_client() as client:
            response = client.post(
                API_URL,
                headers=HEADERS,
                data=json.dumps(
                    {"phone_number": {"country_code": "+91", "phone_number": "999999999"}, "otp_code": 1111}
                ),
            )
            assert response.status_code == 404
            assert response.json
            assert response.json.get("code") == AccountErrorCode.NOT_FOUND

    def test_get_access_token_with_expired_otp(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number))
        )

        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id
        )

        AuthenticationService.verify_otp(
            params=VerifyOTPParams(phone_number=PhoneNumber(**phone_number), otp_code=otp.otp_code)
        )

        with app.test_client() as client:
            response = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"otp_code": otp.otp_code, "phone_number": phone_number})
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == OTPErrorCode.OTP_EXPIRED
            assert response.json.get("message") == "The OTP has expired. Please request a new OTP."

    def test_otp_based_auth_flow_with_disabled_sms_preferences(self):
        """Test complete OTP authentication flow works with disabled SMS preferences"""
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}

        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number))
        )

        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=CreateOrUpdateAccountNotificationPreferencesParams(sms_enabled=False)
        )

        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id
        )

        with app.test_client() as client:
            response = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"phone_number": phone_number, "otp_code": otp.otp_code})
            )

            assert response.status_code == 201
            assert response.json
            assert response.json.get("token")
            assert response.json.get("account_id") == account.id
            assert response.json.get("expires_at")
