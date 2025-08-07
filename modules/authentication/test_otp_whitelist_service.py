import os
from unittest import mock

from modules.authentication.internals.otp.otp_util import OTPUtil
from modules.config.config_service import ConfigService
from modules.config.internals.config_manager import ConfigManager
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken


class TestOTPWhitelistService(BaseTestAccessToken):

    def setUp(self):
        self.original_env = {}
        env_vars = ["DEFAULT_OTP_ENABLED", "DEFAULT_OTP_CODE", "DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"]
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

    def test_default_otp_disabled_with_whitelist_matching_should_use_random(self):
        """When default OTP is disabled and phone matches whitelist, should still use random OTP (send SMS)"""
        os.environ["DEFAULT_OTP_ENABLED"] = ""
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertFalse(result)

    def test_default_otp_disabled_with_whitelist_non_matching_should_use_random(self):
        """When default OTP is disabled and phone doesn't match whitelist, should use random OTP (send SMS)"""
        os.environ["DEFAULT_OTP_ENABLED"] = ""
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("8888888888")
        self.assertFalse(result)

    def test_default_otp_enabled_empty_string_whitelist_should_use_default(self):
        """When default OTP is enabled and whitelist is empty string, should use default OTP (no SMS)"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = ""
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertTrue(result)

    def test_default_otp_enabled_with_whitelist_matching_should_use_default(self):
        """When default OTP is enabled and phone matches whitelist, should use default OTP (no SMS)"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("9999999999")
        self.assertTrue(result)

    def test_default_otp_enabled_with_whitelist_non_matching_should_use_random(self):
        """When default OTP is enabled and phone doesn't match whitelist, should use random OTP (send SMS)"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        result = OTPUtil.should_use_default_otp_for_phone_number("8888888888")
        self.assertFalse(result)

    def test_generate_otp_uses_default_when_should_use_default_is_true(self):
        """When should_use_default_otp_for_phone_number returns True, generate_otp should return default OTP"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        otp = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertEqual(otp, "1234")

    def test_generate_otp_uses_random_when_should_use_default_is_false(self):
        """When should_use_default_otp_for_phone_number returns False, generate_otp should return random OTP"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        otp = OTPUtil.generate_otp(length=4, phone_number="8888888888")
        self.assertNotEqual(otp, "1234")
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())

    def test_generate_otp_uses_random_when_default_otp_disabled(self):
        """When default OTP is disabled, generate_otp should always return random OTP"""
        os.environ["DEFAULT_OTP_ENABLED"] = ""
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        otp = OTPUtil.generate_otp(length=4, phone_number="9999999999")
        self.assertNotEqual(otp, "1234")
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())
