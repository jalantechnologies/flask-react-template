import json
import os
from unittest import mock
from unittest.mock import MagicMock

from web_app import app

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByPhoneNumberParams, PhoneNumber
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from modules.config.config_service import ConfigService
from modules.config.internal.config_manager import ConfigManager
from modules.notification.sms_service import SMSService
from tests.conftest import TEST_ACTOR
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestOTPWhitelistApi(BaseTestAccessToken):

    def setUp(self) -> None:
        self.original_env = {}
        env_vars = ["DEFAULT_OTP_ENABLED", "DEFAULT_OTP_CODE", "DEFAULT_OTP_WHITELISTED_PHONE_NUMBER", "SMS_ENABLED"]
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
        self.original_config_manager = ConfigService.config_manager

    def tearDown(self) -> None:
        for var, value in self.original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value
        ConfigService.config_manager = self.original_config_manager

    def _reload_config(self) -> None:
        ConfigService.config_manager = ConfigManager()

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_default_otp_disabled_matching_whitelist_sends_sms(self, mock_send_sms: MagicMock) -> None:
        """When default OTP is disabled and phone matches whitelist, should still send SMS with random OTP"""
        os.environ["DEFAULT_OTP_ENABLED"] = ""
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            assert response.json is not None
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
            self.assertIn("id", response.json)
            self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_default_otp_disabled_non_matching_whitelist_sends_sms(self, mock_send_sms: MagicMock) -> None:
        """When default OTP is disabled and phone doesn't match whitelist, should send SMS with random OTP"""
        os.environ["DEFAULT_OTP_ENABLED"] = ""
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "8888888888"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            assert response.json is not None
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "8888888888"})
            self.assertIn("id", response.json)
            self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_default_otp_enabled_matching_whitelist_no_sms(self, mock_send_sms: MagicMock) -> None:
        """When default OTP is enabled and phone matches whitelist, should not send SMS"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            assert response.json is not None
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "9999999999"})
            self.assertIn("id", response.json)
            self.assertFalse(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_default_otp_enabled_non_matching_whitelist_sends_sms(self, mock_send_sms: MagicMock) -> None:
        """When default OTP is enabled and phone doesn't match whitelist, should send SMS with random OTP"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        payload = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "8888888888"}})
        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=payload)
            assert response.json is not None
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json.get("phone_number"), {"country_code": "+91", "phone_number": "8888888888"})
            self.assertIn("id", response.json)
            self.assertTrue(mock_send_sms.called)
            self.assertEqual(
                mock_send_sms.call_args.kwargs["params"].recipient_phone,
                PhoneNumber(country_code="+91", phone_number="8888888888"),
            )

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_create_otp_directly_default_enabled_matching_whitelist(self, mock_send_sms: MagicMock) -> None:
        """When calling create_otp directly with enabled default OTP and matching whitelist, should not send SMS"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=phone_number), account_id="test_account_id", actor=TEST_ACTOR
        )

        self.assertEqual(otp.otp_code, "1234")
        self.assertEqual(otp.phone_number, phone_number)
        self.assertFalse(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_create_otp_directly_default_enabled_non_matching_whitelist(self, mock_send_sms: MagicMock) -> None:
        """When calling create_otp directly with enabled default OTP and non-matching whitelist, should send SMS"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        phone_number = PhoneNumber(country_code="+91", phone_number="8888888888")
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=phone_number), account_id="test_account_id", actor=TEST_ACTOR
        )

        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertEqual(otp.phone_number, phone_number)
        self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_create_otp_directly_default_disabled(self, mock_send_sms: MagicMock) -> None:
        """When calling create_otp directly with disabled default OTP, should always send SMS"""
        os.environ["DEFAULT_OTP_ENABLED"] = ""
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = "9999999999"
        self._reload_config()

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=phone_number), account_id="test_account_id", actor=TEST_ACTOR
        )

        self.assertNotEqual(otp.otp_code, "1234")
        self.assertEqual(len(otp.otp_code), 4)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertEqual(otp.phone_number, phone_number)
        self.assertTrue(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_empty_string_whitelist_treated_as_no_whitelist(self, mock_send_sms: MagicMock) -> None:
        """When whitelist is empty string, should treat as no whitelist (use default OTP for all)"""
        os.environ["DEFAULT_OTP_ENABLED"] = "true"
        os.environ["DEFAULT_OTP_CODE"] = "1234"
        os.environ["DEFAULT_OTP_WHITELISTED_PHONE_NUMBER"] = ""
        self._reload_config()

        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=phone_number), account_id="test_account_id", actor=TEST_ACTOR
        )

        self.assertEqual(otp.otp_code, "1234")
        self.assertEqual(otp.phone_number, phone_number)
        self.assertFalse(mock_send_sms.called)

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_otp_creation_uses_bypass_preferences(self, mock_send_sms: MagicMock) -> None:
        """Test that OTP creation uses bypass_preferences=True for SMS"""
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number), actor=TEST_ACTOR
        )

        mock_send_sms.reset_mock()

        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=phone_number), account_id=account.id, actor=TEST_ACTOR
        )

        mock_send_sms.assert_called_once()
        call_kwargs = mock_send_sms.call_args.kwargs
        assert call_kwargs["bypass_preferences"] is True
        assert call_kwargs["account_id"] == account.id
