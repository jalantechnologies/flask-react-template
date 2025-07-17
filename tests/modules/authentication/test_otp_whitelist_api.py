import os
import json
from unittest.mock import patch, MagicMock
from typing import Callable

from server import app
from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByPhoneNumberParams, PhoneNumber
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestOTPWhitelistAPI(BaseTestAccessToken):
    def setup_method(self, method: Callable) -> None:
        super().setup_method(method)

    def teardown_method(self, method: Callable) -> None:
        super().teardown_method(method)
        env_vars_to_clean = [
            "DEFAULT_OTP_ENABLED",
            "DEFAULT_OTP_CODE",
            "DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE",
        ]
        for var in env_vars_to_clean:
            os.environ.pop(var, None)

    @patch("modules.notification.internals.twilio_service.Client")
    def test_account_creation_with_whitelisted_number_uses_default_otp(self, mock_twilio_client) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = "9999999999,8888888888"

        mock_client_instance = MagicMock()
        mock_twilio_client.return_value = mock_client_instance

        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
            mock_client_instance.messages.create.assert_not_called()

    @patch("modules.notification.internals.twilio_service.Client")
    def test_account_creation_with_non_whitelisted_number_sends_sms(self, mock_twilio_client) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = "9999999999,8888888888"

        mock_client_instance = MagicMock()
        mock_twilio_client.return_value = mock_client_instance

        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "7777777777"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "7777777777"})
            mock_client_instance.messages.create.assert_called_once()

    @patch("modules.notification.internals.twilio_service.Client")
    def test_access_token_creation_with_non_whitelisted_number_random_otp(self, mock_twilio_client) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = "9999999999,8888888888"

        mock_client_instance = MagicMock()
        mock_twilio_client.return_value = mock_client_instance

        phone_number = PhoneNumber(country_code="+91", phone_number="7777777777")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "7777777777"}, "otp_code": otp.otp_code}
        )
        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertIn("token", response.json)
            self.assertEqual(response.json.get("account_id"), account.id)
            self.assertIn("expires_at", response.json)

    def test_access_token_creation_with_wrong_default_otp_for_non_whitelisted_number(self) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = "9999999999,8888888888"

        phone_number = PhoneNumber(country_code="+91", phone_number="7777777777")
        AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "7777777777"}, "otp_code": "1234"}
        )
        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn("code", response.json)
            self.assertEqual(response.json.get("message"), "Please provide the correct OTP to login.")

    def test_access_token_creation_with_disabled_default_otp(self) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "false"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = "9999999999,8888888888"

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "9999999999"}, "otp_code": "1234"}
        )
        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn("code", response.json)
            self.assertEqual(response.json.get("message"), "Please provide the correct OTP to login.")

    def test_access_token_creation_with_empty_whitelist(self) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = ""

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "9999999999"}, "otp_code": "1234"}
        )
        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn("code", response.json)
            self.assertEqual(response.json.get("message"), "Please provide the correct OTP to login.")

    def test_multiple_whitelisted_numbers_work(self) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = "9999999999,8888888888,7777777777"

        for number in ["9999999999", "8888888888", "7777777777"]:
            with self.subTest(number=number):
                phone_number = PhoneNumber(country_code="+91", phone_number=number)
                account = AccountService.get_or_create_account_by_phone_number(
                    params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
                )
                payload = json.dumps(
                    {"phone_number": {"country_code": "+91", "phone_number": number}, "otp_code": "1234"}
                )
                with app.test_client() as client:
                    response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)
                    self.assertEqual(response.status_code, 201)
                    self.assertIn("token", response.json)
                    self.assertEqual(response.json.get("account_id"), account.id)
                    self.assertIn("expires_at", response.json)

    def test_case_sensitivity_in_whitelist(self) -> None:
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBERS_WITH_COUNTRY_CODE"] = "9999999999"

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "9999999999"}, "otp_code": "1234"}
        )
        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertIn("token", response.json)
            self.assertEqual(response.json.get("account_id"), account.id)
