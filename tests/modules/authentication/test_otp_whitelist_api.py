import json
from unittest.mock import patch
from typing import Callable

from server import app
from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByPhoneNumberParams, PhoneNumber
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams, VerifyOTPParams
from modules.config.config_service import ConfigService
from modules.notification.sms_service import SMSService
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestOTPWhitelistAPI(BaseTestAccessToken):
    def setup_method(self, method: Callable) -> None:
        super().setup_method(method)

    def teardown_method(self, method: Callable) -> None:
        super().teardown_method(method)

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_account_creation_with_whitelisted_number_uses_default_otp(self, mock_get_value, mock_send_sms) -> None:
        """Test that account creation with whitelisted number uses default OTP and doesn't send SMS"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with whitelisted phone number
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)

            # Verify account creation was successful
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})

            # Verify SMS was not sent for whitelisted number
            # Note: get_or_create_account_by_phone_number internally calls create_otp which doesn't send SMS for whitelisted numbers
            mock_send_sms.assert_not_called()

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_account_creation_with_non_whitelisted_number_sends_sms(self, mock_get_value, mock_send_sms) -> None:
        """Test that account creation with non-whitelisted number sends SMS"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with non-whitelisted phone number
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "7777777777"}})

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)

            # Verify account creation was successful
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "7777777777"})

            # Verify SMS was sent for non-whitelisted number
            # Note: get_or_create_account_by_phone_number internally calls create_otp which sends SMS for non-whitelisted numbers
            mock_send_sms.assert_called_once()

    @patch.object(ConfigService, "get_value")
    def test_access_token_creation_with_whitelisted_number_default_otp(self, mock_get_value) -> None:
        """Test that access token can be created using default OTP for whitelisted number"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with whitelisted phone number
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        # Try to get access token using default OTP
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "9999999999"}, "otp_code": "1234"}  # Default OTP
        )

        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)

            # Verify access token creation was successful
            self.assertEqual(response.status_code, 201)
            self.assertIn("token", response.json)
            self.assertEqual(response.json.get("account_id"), account.id)
            self.assertIn("expires_at", response.json)

    @patch.object(ConfigService, "get_value")
    def test_access_token_creation_with_non_whitelisted_number_random_otp(self, mock_get_value) -> None:
        """Test that access token creation with non-whitelisted number requires actual OTP"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with non-whitelisted phone number
        phone_number = PhoneNumber(country_code="+91", phone_number="7777777777")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        # Generate actual OTP
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))

        # Try to get access token using actual OTP
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "7777777777"}, "otp_code": otp.otp_code}
        )

        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)

            # Verify access token creation was successful
            self.assertEqual(response.status_code, 201)
            self.assertIn("token", response.json)
            self.assertEqual(response.json.get("account_id"), account.id)
            self.assertIn("expires_at", response.json)

    @patch.object(ConfigService, "get_value")
    def test_access_token_creation_with_wrong_default_otp_for_non_whitelisted_number(self, mock_get_value) -> None:
        """Test that default OTP doesn't work for non-whitelisted numbers"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with non-whitelisted phone number
        phone_number = PhoneNumber(country_code="+91", phone_number="7777777777")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        # Try to get access token using default OTP (should fail)
        payload = json.dumps(
            {
                "phone_number": {"country_code": "+91", "phone_number": "7777777777"},
                "otp_code": "1234",  # Default OTP should not work
            }
        )

        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)

            # Verify access token creation failed
            self.assertEqual(response.status_code, 400)
            self.assertIn("code", response.json)
            self.assertEqual(response.json.get("message"), "Please provide the correct OTP to login.")

    @patch.object(ConfigService, "get_value")
    def test_access_token_creation_with_disabled_default_otp(self, mock_get_value) -> None:
        """Test that default OTP doesn't work when feature is disabled"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": False,  # Disabled
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with whitelisted phone number
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        # Try to get access token using default OTP (should fail when disabled)
        payload = json.dumps(
            {
                "phone_number": {"country_code": "+91", "phone_number": "9999999999"},
                "otp_code": "1234",  # Default OTP should not work when disabled
            }
        )

        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)

            # Verify access token creation failed
            self.assertEqual(response.status_code, 400)
            self.assertIn("code", response.json)
            self.assertEqual(response.json.get("message"), "Please provide the correct OTP to login.")

    @patch.object(ConfigService, "get_value")
    def test_access_token_creation_with_empty_whitelist(self, mock_get_value) -> None:
        """Test that default OTP doesn't work with empty whitelist"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": [],  # Empty whitelist
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with phone number
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        # Try to get access token using default OTP (should fail with empty whitelist)
        payload = json.dumps(
            {
                "phone_number": {"country_code": "+91", "phone_number": "9999999999"},
                "otp_code": "1234",  # Default OTP should not work with empty whitelist
            }
        )

        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)

            # Verify access token creation failed
            self.assertEqual(response.status_code, 400)
            self.assertIn("code", response.json)
            self.assertEqual(response.json.get("message"), "Please provide the correct OTP to login.")

    @patch.object(ConfigService, "get_value")
    def test_multiple_whitelisted_numbers_work(self, mock_get_value) -> None:
        """Test that multiple whitelisted numbers all work with default OTP"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888", "7777777777"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        whitelisted_numbers = ["9999999999", "8888888888", "7777777777"]

        for number in whitelisted_numbers:
            with self.subTest(number=number):
                # Create account with whitelisted phone number
                phone_number = PhoneNumber(country_code="+91", phone_number=number)
                account = AccountService.get_or_create_account_by_phone_number(
                    params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
                )

                # Try to get access token using default OTP
                payload = json.dumps(
                    {"phone_number": {"country_code": "+91", "phone_number": number}, "otp_code": "1234"}
                )

                with app.test_client() as client:
                    response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)

                    # Verify access token creation was successful
                    self.assertEqual(response.status_code, 201)
                    self.assertIn("token", response.json)
                    self.assertEqual(response.json.get("account_id"), account.id)
                    self.assertIn("expires_at", response.json)

    @patch.object(ConfigService, "get_value")
    def test_case_sensitivity_in_whitelist(self, mock_get_value) -> None:
        """Test that whitelist matching is case sensitive (if applicable)"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999"],  # Exact match required
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with phone number that matches whitelist
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        # Try to get access token using default OTP
        payload = json.dumps(
            {"phone_number": {"country_code": "+91", "phone_number": "9999999999"}, "otp_code": "1234"}
        )

        with app.test_client() as client:
            response = client.post(ACCESS_TOKEN_URL, headers=HEADERS, data=payload)

            # Verify access token creation was successful
            self.assertEqual(response.status_code, 201)
            self.assertIn("token", response.json)
            self.assertEqual(response.json.get("account_id"), account.id)
