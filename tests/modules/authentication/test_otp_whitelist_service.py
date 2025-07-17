import os
from unittest import mock

from modules.authentication.internals.otp.otp_util import OTPUtil
from modules.config.config_service import ConfigService
from modules.config.internals.config_manager import ConfigManager
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken


class TestOTPWhitelistService(BaseTestAccessToken):

    def setUp(self):
        self.original_env = {}
        env_vars = ["DEFAULT_OTP_ENABLED", "DEFAULT_OTP_CODE", "DEFAULT_OTP_WHITELISTED_NUMBER"]
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)

        self.original_config_manager = ConfigService.config_manager

    def tearDown(self):
        for var, value in self.original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

        ConfigService.config_manager = self.original_config_manager

    def _reload_config(self):
        ConfigService.config_manager = ConfigManager()

    def test_should_use_default_otp_when_enabled_and_no_whitelist(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ.pop("DEFAULT_OTP_WHITELISTED_NUMBER", None)
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertTrue(result)

    def test_should_not_use_default_otp_when_disabled(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "8888888888"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertFalse(result)

        result = OTPUtil.should_use_default_otp_for_phone_number("8888888888")
        self.assertTrue(result)

    def test_generate_otp_uses_random_when_not_whitelisted(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "8888888888,7777777777"
        self._reload_config()

        otp = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertNotEqual(otp, "1234")
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())

        otp = OTPUtil.generate_otp(length=4, phone_number="8888888888")
        self.assertEqual(otp, "1234")

    def test_should_not_use_default_otp_for_non_whitelisted_number(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "9999999999,8888888888"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("7777777777")
        self.assertFalse(result)

    def test_should_not_use_default_otp_for_empty_whitelist(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = ""
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertFalse(result)

    def test_should_not_use_default_otp_for_partial_match(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "99999"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertFalse(result)

        result = OTPUtil.should_use_default_otp_for_phone_number("99999")
        self.assertTrue(result)

    def test_should_handle_single_number_whitelist(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "9999999999"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertTrue(result)

        result = OTPUtil.should_use_default_otp_for_phone_number("8888888888")
        self.assertFalse(result)

    def test_generate_otp_uses_default_for_whitelisted_number(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "9999999999"
        self._reload_config()

        otp = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertEqual(otp, "1234")

        otp = OTPUtil.generate_otp(length=4, phone_number="7777777777")
        self.assertNotEqual(otp, "1234")
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())

    def test_generate_otp_uses_default_when_no_whitelist(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ.pop("DEFAULT_OTP_WHITELISTED_NUMBER", None)
        self._reload_config()

        otp = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertEqual(otp, "1234")

        otp = OTPUtil.generate_otp(length=4, phone_number="7777777777")
        self.assertEqual(otp, "1234")

    def test_generate_otp_uses_random_when_not_whitelisted_comprehensive(self):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "8888888888"
        self._reload_config()

        otp = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertNotEqual(otp, "1234")
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())

        otp = OTPUtil.generate_otp(length=4, phone_number="8888888888")
        self.assertEqual(otp, "1234")

    def test_case_sensitivity_in_boolean_config(self):
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_NUMBER"] = "9999999999"
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        self._reload_config()
        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertTrue(result, "Whitelisted number should use default OTP")

        result = OTPUtil.should_use_default_otp_for_phone_number("8888888888")
        self.assertFalse(result, "Non-whitelisted number should not use default OTP")
