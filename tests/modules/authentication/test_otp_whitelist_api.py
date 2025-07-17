import json
import os
from unittest import mock

from server import app
from modules.account.types import PhoneNumber
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from modules.config.config_service import ConfigService
from modules.config.internals.config_manager import ConfigManager
from modules.notification.sms_service import SMSService
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestOTPWhitelistApi(BaseTestAccessToken):

    def setUp(self):
        self.original_env = {}
        env_vars = [
            "DEFAULT_OTP_ENABLED",
            "DEFAULT_OTP_CODE",
            "DEFAULT_OTP_WHITELISTED_PHONE_NUMBER",
            "SMS_ENABLED",
        ]
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

    @mock.patch.object(SMSService, "send_sms")
    def test_create_account_with_whitelisted_phone_number_no_sms(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999,8888888888"
        self._reload_config()
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
            self.assertIn("id", response.json)
            self.assertFalse(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms")
    def test_create_account_with_non_whitelisted_phone_number_sends_sms(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999,8888888888"
        self._reload_config()
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "7777777777"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "7777777777"})
            self.assertIn("id", response.json)
            self.assertTrue(mock_send_sms.called)
            self.assertEqual(
                mock_send_sms.call_args.kwargs["params"].recipient_phone,
                PhoneNumber(country_code="+91", phone_number="7777777777"),
            )

    @mock.patch.object(SMSService, "send_sms")
    def test_create_account_default_otp_disabled_sends_sms(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "8888888888,7777777777"
        self._reload_config()
        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
            self.assertIn("id", response.json)
            self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms")
    def test_sms_service_behavior_when_disabled_config(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "8888888888"
        self._reload_config()
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))
        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertEqual(otp.phone_number, phone_number)
        self.assertTrue(mock_send_sms.called)
        self.assertEqual(mock_send_sms.call_args.kwargs["params"].recipient_phone, phone_number)

    @mock.patch.object(SMSService, "send_sms")
    def test_create_otp_directly_with_whitelisted_number(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999,8888888888"
        self._reload_config()
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))
        self.assertEqual(otp.otp_code, "1234")
        self.assertEqual(otp.phone_number, phone_number)
        self.assertFalse(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms")
    def test_create_otp_directly_with_non_whitelisted_number(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999,8888888888"
        self._reload_config()
        phone_number = PhoneNumber(country_code="+91", phone_number="7777777777")
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))
        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertEqual(otp.phone_number, phone_number)
        self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms")
    def test_whitelist_with_empty_string_config(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = ""
        self._reload_config()
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))
        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertEqual(otp.phone_number, phone_number)
        self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms")
    def test_whitelist_partial_match_does_not_work(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "99999"
        self._reload_config()
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number))
        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertEqual(otp.phone_number, phone_number)
        self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms")
    def test_multiple_whitelisted_numbers(self, mock_send_sms):
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999,8888888888,7777777777"
        self._reload_config()
        phone_number_1 = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp_1 = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number_1))
        self.assertEqual(otp_1.otp_code, "1234")
        phone_number_2 = PhoneNumber(country_code="+91", phone_number="8888888888")
        otp_2 = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number_2))
        self.assertEqual(otp_2.otp_code, "1234")
        phone_number_3 = PhoneNumber(country_code="+91", phone_number="7777777777")
        otp_3 = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number_3))
        self.assertEqual(otp_3.otp_code, "1234")
        phone_number_4 = PhoneNumber(country_code="+91", phone_number="6666666666")
        otp_4 = AuthenticationService.create_otp(params=CreateOTPParams(phone_number=phone_number_4))
        self.assertNotEqual(otp_4.otp_code, "1234")
        self.assertTrue(mock_send_sms.called)
        self.assertEqual(mock_send_sms.call_count, 1)
