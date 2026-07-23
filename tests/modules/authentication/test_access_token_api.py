import json
from datetime import UTC, datetime, timedelta
from unittest import mock

from server import app

from modules.account.account_service import AccountService
from modules.account.internal.account_writer import AccountWriter
from modules.account.internal.password_hash import PasswordHash
from modules.account.types import (
    AccountErrorCode,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams, OTPErrorCode, VerifyOTPParams
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from tests.conftest import TEST_ACTOR
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken

API_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestAccessTokenApi(BaseTestAccessToken):
    def test_get_access_token_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
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
            ),
            actor=TEST_ACTOR,
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
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccountErrorCode.INVALID_CREDENTIALS

    def test_get_access_token_with_invalid_username_and_password(self) -> None:
        with app.test_client() as client:
            response = client.post(
                API_URL,
                headers=HEADERS,
                data=json.dumps({"username": "invalid_username", "password": "invalid_password"}),
            )
            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccountErrorCode.INVALID_CREDENTIALS

    def test_unknown_username_and_wrong_password_return_byte_identical_responses(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            unknown_username = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"username": "nobody", "password": "password"})
            )
            wrong_password = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"username": account.username, "password": "wrong_password"})
            )

        assert unknown_username.status_code == 401
        assert wrong_password.status_code == 401
        assert unknown_username.data == wrong_password.data

    def test_unknown_username_still_verifies_a_password_hash(self) -> None:
        with mock.patch.object(PasswordHash, "matches", return_value=False) as mock_matches:
            with app.test_client() as client:
                response = client.post(
                    API_URL, headers=HEADERS, data=json.dumps({"username": "nobody", "password": "password"})
                )

        assert response.status_code == 401
        mock_matches.assert_called_once()

    def test_given_phone_number_when_creating_one_time_password_then_created_at_and_updated_at_reflect_creation_time(
        self,
    ) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )

        before = datetime.now(UTC)
        one_time_password = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
        )
        after = datetime.now(UTC)

        assert one_time_password.created_at is not None
        assert one_time_password.updated_at is not None
        assert one_time_password.created_at.tzinfo is not None
        assert one_time_password.updated_at.tzinfo is not None
        assert one_time_password.created_at.utcoffset() == timedelta(0)
        assert one_time_password.updated_at.utcoffset() == timedelta(0)
        assert one_time_password.created_at == one_time_password.updated_at
        assert before <= one_time_password.created_at <= after
        assert before <= one_time_password.updated_at <= after

    def test_given_existing_one_time_password_when_verifying_then_updated_at_reflects_verification_time(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )
        one_time_password = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
        )

        before = datetime.now(UTC)
        verified_one_time_password = AuthenticationService.verify_otp(
            params=VerifyOTPParams(phone_number=PhoneNumber(**phone_number), otp_code=one_time_password.otp_code),
            account_id=account.id,
            actor=TEST_ACTOR,
        )
        after = datetime.now(UTC)

        assert verified_one_time_password.updated_at is not None
        assert verified_one_time_password.created_at is not None
        assert before - timedelta(milliseconds=1) <= verified_one_time_password.updated_at <= after
        assert verified_one_time_password.updated_at > verified_one_time_password.created_at

    def test_get_access_token_by_phone_number_and_otp(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )

        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
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
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
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
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )

        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
        )

        AuthenticationService.verify_otp(
            params=VerifyOTPParams(phone_number=PhoneNumber(**phone_number), otp_code=otp.otp_code),
            account_id=account.id,
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            response = client.post(
                API_URL, headers=HEADERS, data=json.dumps({"otp_code": otp.otp_code, "phone_number": phone_number})
            )
            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == OTPErrorCode.OTP_EXPIRED
            assert response.json.get("message") == "The OTP has expired. Please request a new OTP."

    def test_otp_based_auth_flow_with_disabled_sms_preferences(self) -> None:
        """Test complete OTP authentication flow works with disabled SMS preferences"""
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}

        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )

        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id,
            actor=TEST_ACTOR,
            preferences=CreateOrUpdateAccountNotificationPreferencesParams(sms_enabled=False),
        )

        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
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
