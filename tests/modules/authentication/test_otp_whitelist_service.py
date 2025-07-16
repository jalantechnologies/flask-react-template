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
        self.original_config = {}

    def teardown_method(self, method: Callable) -> None:
        super().teardown_method(method)

    @patch.object(ConfigService, "get_value")
    def test_generate_otp_with_whitelisted_number(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        otp_code = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertEqual(otp_code, "1234")

        otp_code = OTPUtil.generate_otp(length=4, phone_number="8888888888")
        self.assertEqual(otp_code, "1234")

    @patch.object(ConfigService, "get_value")
    def test_generate_otp_with_non_whitelisted_number(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        otp_code = OTPUtil.generate_otp(length=4, phone_number="7777777777")
        self.assertNotEqual(otp_code, "1234")
        self.assertEqual(len(otp_code), 4)
        self.assertTrue(otp_code.isdigit())

    @patch.object(ConfigService, "get_value")
    def test_generate_otp_with_default_otp_disabled(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": False,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        otp_code = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertNotEqual(otp_code, "1234")
        self.assertEqual(len(otp_code), 4)
        self.assertTrue(otp_code.isdigit())

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_whitelisted_number(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        result = OTPUtil.is_phone_number_whitelisted_for_default_otp("9999999999")
        self.assertTrue(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_non_whitelisted_number(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        result = OTPUtil.is_phone_number_whitelisted_for_default_otp("7777777777")
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_when_disabled(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": False,
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        result = OTPUtil.is_phone_number_whitelisted_for_default_otp("9999999999")
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_empty_whitelist(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.whitelisted_phone_numbers_with_country_code": [],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        result = OTPUtil.is_phone_number_whitelisted_for_default_otp("9999999999")
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    def test_is_default_otp_enabled_with_none_phone_number(self, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        result = OTPUtil.is_phone_number_whitelisted_for_default_otp(None)
        self.assertFalse(result)

    @patch.object(ConfigService, "get_value")
    @patch("modules.logger.logger.Logger.warn")
    def test_is_default_otp_enabled_with_invalid_config(self, mock_warn, mock_get_value) -> None:

        def mock_config_side_effect(key, default=None):
            if key == "public.default_otp.enabled":
                return True
            if key == "public.default_otp.whitelisted_phone_numbers_with_country_code":
                raise ValueError("Invalid configuration")
            if key == "accounts.token_signing_key":
                return "JWT_TOKEN"
            if key == "accounts.token_expiry_days":
                return 1
            return default

        mock_get_value.side_effect = mock_config_side_effect

        result = OTPUtil.is_phone_number_whitelisted_for_default_otp("9999999999")
        self.assertFalse(result)
        mock_warn.assert_called_once()

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_create_otp_does_not_send_sms_for_whitelisted_number(self, mock_get_value, mock_send_sms) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        mock_send_sms.reset_mock()

        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))

        self.assertEqual(otp.otp_code, "1234")

        mock_send_sms.assert_not_called()

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_create_otp_sends_sms_for_non_whitelisted_number(self, mock_get_value, mock_send_sms) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": True,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        phone_number = PhoneNumber(country_code="+91", phone_number="7777777777")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        mock_send_sms.reset_mock()

        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))

        self.assertNotEqual(otp.otp_code, "1234")

        mock_send_sms.assert_called_once()

        call_args = mock_send_sms.call_args
        sms_params = call_args.kwargs["params"]
        self.assertEqual(sms_params.recipient_phone, phone_number)
        self.assertIn("is your One Time Password (OTP) for verification", sms_params.message_body)

    @patch.object(SMSService, "send_sms")
    @patch.object(ConfigService, "get_value")
    def test_create_otp_sends_sms_when_default_otp_disabled(self, mock_get_value, mock_send_sms) -> None:

        def mock_config_side_effect(key, default=None):
            config_values = {
                "public.default_otp.enabled": False,
                "public.default_otp.code": "1234",
                "public.default_otp.whitelisted_phone_numbers_with_country_code": ["9999999999", "8888888888"],
                "accounts.token_signing_key": "JWT_TOKEN",
                "accounts.token_expiry_days": 1,
            }
            return config_values.get(key, default)

        mock_get_value.side_effect = mock_config_side_effect

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        mock_send_sms.reset_mock()

        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))

        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())

        mock_send_sms.assert_called_once()
