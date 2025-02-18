import json
from datetime import datetime, timedelta
from unittest import mock

import jwt

from modules.access_token.types import AccessTokenErrorCode
from modules.account.account_service import AccountService
from modules.account.types import (
    AccountErrorCode,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.communication.sms_service import SMSService
from modules.config.config_service import ConfigService
from modules.otp.types import OtpErrorCode
from server import app
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestAccountApi(BaseTestAccount):
    def test_create_account_by_username_and_password(self) -> None:
        payload = json.dumps(
            {"first_name": "first_name", "last_name": "last_name", "password": "password", "username": "username"}
        )

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            assert response.status_code == 201
            assert response.json, f"No response from API with status code:: {response.status}"
            assert response.json.get("username") == "username"

    def test_create_account_with_existing_user(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )
        with app.test_client() as client:
            response = client.post(
                ACCOUNT_URL,
                headers=HEADERS,
                data=json.dumps(
                    {
                        "first_name": "first_name",
                        "last_name": "last_name",
                        "password": "password",
                        "username": account.username,
                    }
                ),
            )
        assert response.status_code == 409
        assert response.json
        assert response.json.get("code") == AccountErrorCode.USERNAME_ALREADY_EXISTS

    @mock.patch.object(SMSService, "send_sms")
    def test_create_account_by_phone_number_and_send_otp(self, mock_send_sms) -> None:
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
            self.assertIn("id", response.json)
            self.assertTrue(mock_send_sms.called)
            self.assertEqual(
                mock_send_sms.call_args.kwargs["params"].recipient_phone,
                PhoneNumber(country_code="+91", phone_number="9999999999"),
            )
            self.assertIn(
                "is your One Time Password (OTP) for verification.",
                mock_send_sms.call_args.kwargs["params"].message_body,
            )

    @mock.patch.object(SMSService, "send_sms")
    def test_get_account_with_existing_phone_number_and_send_otp(self, mock_send_sms) -> None:
        AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**{"country_code": "+91", "phone_number": "9999999999"}))
        )
        with app.test_client() as client:
            response = client.post(
                ACCOUNT_URL,
                headers=HEADERS,
                data=json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}}),
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
        self.assertIn("id", response.json)
        self.assertTrue(mock_send_sms.called)
        self.assertEqual(
            mock_send_sms.call_args.kwargs["params"].recipient_phone,
            PhoneNumber(country_code="+91", phone_number="9999999999"),
        )
        self.assertIn(
            "is your One Time Password (OTP) for verification.", mock_send_sms.call_args.kwargs["params"].message_body
        )

    @mock.patch.object(SMSService, "send_sms")
    def test_get_or_create_account_with_invalid_phone_number(self, mock_send_sms) -> None:
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "999999999"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 400)
            self.assertTrue(response.json)
            self.assertEqual(response.json.get("code"), OtpErrorCode.REQUEST_FAILED)
            self.assertEqual(response.json.get("message"), "Please provide a valid phone number.")
            self.assertFalse(mock_send_sms.called)

    def test_get_account_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            access_token = client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )
            response = client.get(
                f"http://127.0.0.1:8080/api/accounts/{account.id}",
                headers={"Authorization": f"Bearer {access_token.json.get('token')}"},
            )
            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == account.id
            assert response.json.get("username") == account.username
            assert response.json.get("first_name") == account.first_name
            assert response.json.get("last_name") == account.last_name

    def test_get_account_by_username_and_password_with_invalid_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            client.post(
                "http://127.0.0.1:8080/api/access-tokens",
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )
            response = client.get(
                f"http://127.0.0.1:8080/api/accounts/{account.id}", headers={"Authorization": f"Bearer invalid_token"}
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_get_account_with_expired_access_token(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        # Create an expired token by setting the expiry to a date in the past using same method as in the
        # access token service
        jwt_signing_key = ConfigService.get_token_signing_key()
        jwt_expiry = timedelta(days=ConfigService.get_token_expiry_days() - 1)
        payload = {"account_id": account.id, "exp": (datetime.now() - jwt_expiry).timestamp()}
        expired_token = jwt.encode(payload, jwt_signing_key, algorithm="HS256")

        with app.test_client() as client:
            response = client.get(
                f"http://127.0.0.1:8080/api/accounts/{account.id}", headers={"Authorization": f"Bearer {expired_token}"}
            )

            assert response.status_code == 401
            assert "Access token has expired. Please login again." in response.json.get("message", "")
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_EXPIRED
