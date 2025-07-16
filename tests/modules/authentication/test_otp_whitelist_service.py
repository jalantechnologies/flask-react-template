import unittest
from unittest.mock import MagicMock, patch
from typing import Callable

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByPhoneNumberParams, PhoneNumber
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.internals.otp.otp_util import OTPUtil
from modules.authentication.types import CreateOTPParams
from modules.config.config_service import ConfigService
from modules.notification.sms_service import SMSService
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken


class TestOTPWhitelistService(BaseTestAccessToken):
    def setup_method(self, method: Callable) -> None:
        super().setup_method(method)
        # Reset any mocked configurations
        self.original_config = {}

    def teardown_method(self, method: Callable) -> None:
        super().teardown_method(method)
        # Restore original config if needed

    @patch.object(ConfigService, "get_value")
    def test_generate_otp_with_whitelisted_number(self, mock_get_value) -> None:
        """Test that whitelisted phone numbers get default OTP code"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Test with whitelisted number
        otp_code = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertEqual(otp_code, "1234")

        # Test with another whitelisted number
        otp_code = OTPUtil.generate_otp(length=4, phone_number="8888888888")
        self.assertEqual(otp_code, "1234")

    @patch.object(ConfigService, "get_value")
    def test_generate_otp_with_non_whitelisted_number(self, mock_get_value) -> None:
        """Test that non-whitelisted phone numbers get random OTP code"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Test with non-whitelisted number
        otp_code = OTPUtil.generate_otp(length=4, phone_number="7777777777")
        self.assertNotEqual(otp_code, "1234")
        self.assertEqual(len(otp_code), 4)
        self.assertTrue(otp_code.isdigit())

    @patch.object(ConfigService, "get_value")
    def test_generate_otp_with_default_otp_disabled(self, mock_get_value) -> None:
        """Test that random OTP is generated when default OTP is disabled"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": False,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Even with whitelisted number, should generate random OTP when disabled
        otp_code = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertNotEqual(otp_code, "1234")
        self.assertEqual(len(otp_code), 4)
        self.assertTrue(otp_code.isdigit())

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_whitelisted_number(self, mock_get_value) -> None:
        """Test is_default_otp_enabled returns True for whitelisted numbers"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Test with whitelisted number
        result = OTPUtil.is_default_otp_enabled("9999999999")
        self.assertTrue(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_non_whitelisted_number(self, mock_get_value) -> None:
        """Test is_default_otp_enabled returns False for non-whitelisted numbers"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Test with non-whitelisted number
        result = OTPUtil.is_default_otp_enabled("7777777777")
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_when_disabled(self, mock_get_value) -> None:
        """Test is_default_otp_enabled returns False when feature is disabled"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": False,
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Even with whitelisted number, should return False when disabled
        result = OTPUtil.is_default_otp_enabled("9999999999")
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_empty_whitelist(self, mock_get_value) -> None:
        """Test is_default_otp_enabled returns False with empty whitelist"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {"public.default_otp.enabled": True, "public.default_otp.whitelist": []}
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Should return False with empty whitelist
        result = OTPUtil.is_default_otp_enabled("9999999999")
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_none_phone_number(self, mock_get_value) -> None:
        """Test is_default_otp_enabled returns False when phone_number is None"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Should return False when phone_number is None
        result = OTPUtil.is_default_otp_enabled(None)
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    @patch("modules.logger.logger.Logger.warn")
    def test_is_default_otp_enabled_with_invalid_config(self, mock_warn, mock_get_value) -> None:
        """Test is_default_otp_enabled handles configuration errors gracefully"""

        # Mock configuration to raise an error
        def mock_config_side_effect(key, default=None):
            if key == "public.default_otp.enabled":
                return True
            if key == "public.default_otp.whitelist":
                raise ValueError("Invalid configuration")
            return default

        mock_get_value.side_effect = mock_config_side_effect

        # Should return False and log warning on error
        result = OTPUtil.is_default_otp_enabled("9999999999")
        self.assertFalse(result)
        mock_warn.assert_called_once()

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_create_otp_does_not_send_sms_for_whitelisted_number(self, mock_get_value, mock_send_sms) -> None:
        """Test that SMS is not sent for whitelisted phone numbers"""

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

        # Reset mock to check only the next call
        mock_send_sms.reset_mock()

        # Create OTP
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))

        # Verify OTP code is default
        self.assertEqual(otp.otp_code, "1234")

        # Verify SMS was not sent
        mock_send_sms.assert_not_called()

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_create_otp_sends_sms_for_non_whitelisted_number(self, mock_get_value, mock_send_sms) -> None:
        """Test that SMS is sent for non-whitelisted phone numbers"""

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

        # Reset mock to check only the next call
        mock_send_sms.reset_mock()

        # Create OTP
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))

        # Verify OTP code is not default
        self.assertNotEqual(otp.otp_code, "1234")

        # Verify SMS was sent
        mock_send_sms.assert_called_once()

        # Verify SMS content
        call_args = mock_send_sms.call_args
        sms_params = call_args.kwargs["params"]
        self.assertEqual(sms_params.recipient_phone, phone_number)
        self.assertIn("is your One Time Password (OTP) for verification", sms_params.message_body)

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_create_otp_sends_sms_when_default_otp_disabled(self, mock_get_value, mock_send_sms) -> None:
        """Test that SMS is always sent when default OTP is disabled"""

        # Mock configuration values
        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": False,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelist": ["9999999999", "8888888888"],
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        # Create account with whitelisted phone number (but feature disabled)
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        # Reset mock to check only the next call
        mock_send_sms.reset_mock()

        # Create OTP
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))

        # Verify OTP code is not default (random)
        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())

        # Verify SMS was sent even for whitelisted number when feature is disabled
        mock_send_sms.assert_called_once()
