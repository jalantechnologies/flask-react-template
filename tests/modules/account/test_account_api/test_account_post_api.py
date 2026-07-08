import json
from unittest import mock

from server import app

from modules.account.account_service import AccountService
from modules.account.types import (
    AccountErrorCode,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.types import OTPErrorCode
from modules.notification.sms_service import SMSService
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestAccountPostApi(BaseTestAccount):
    def test_given_valid_username_and_password_when_creating_account_then_returns_created_account(self) -> None:
        request_body = json.dumps(
            {"first_name": "first_name", "last_name": "last_name", "password": "password", "username": "username"}
        )

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=request_body)

            assert response.status_code == 201
            assert response.json
            assert response.json.get("username") == "username"

    def test_given_existing_username_when_creating_account_then_returns_conflict(self) -> None:
        existing_account = AccountService.create_account_by_username_and_password(
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
                        "username": existing_account.username,
                    }
                ),
            )

            assert response.status_code == 409
            assert response.json
            assert response.json.get("code") == AccountErrorCode.USERNAME_ALREADY_EXISTS

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_given_new_phone_number_when_creating_account_then_creates_account_and_sends_one_time_password(
        self, mock_send_sms
    ) -> None:
        request_body = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}})

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=request_body)

            assert response.status_code == 201
            assert response.json.get("phone_number") == {"country_code": "+91", "phone_number": "9999999999"}
            assert "id" in response.json
            assert mock_send_sms.called
            assert mock_send_sms.call_args.kwargs["params"].recipient_phone == PhoneNumber(
                country_code="+91", phone_number="9999999999"
            )
            assert (
                "is your One Time Password (OTP) for verification."
                in mock_send_sms.call_args.kwargs["params"].message_body
            )

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_given_existing_phone_number_when_creating_account_then_returns_account_and_sends_one_time_password(
        self, mock_send_sms
    ) -> None:
        AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(
                phone_number=PhoneNumber(country_code="+91", phone_number="9999999999")
            )
        )

        with app.test_client() as client:
            response = client.post(
                ACCOUNT_URL,
                headers=HEADERS,
                data=json.dumps({"phone_number": {"country_code": "+91", "phone_number": "9999999999"}}),
            )

            assert response.status_code == 201
            assert response.json.get("phone_number") == {"country_code": "+91", "phone_number": "9999999999"}
            assert "id" in response.json
            assert mock_send_sms.called
            assert mock_send_sms.call_args.kwargs["params"].recipient_phone == PhoneNumber(
                country_code="+91", phone_number="9999999999"
            )
            assert (
                "is your One Time Password (OTP) for verification."
                in mock_send_sms.call_args.kwargs["params"].message_body
            )

    @mock.patch.object(SMSService, "send_sms_for_account")
    def test_given_invalid_phone_number_when_creating_account_then_returns_bad_request(self, mock_send_sms) -> None:
        request_body = json.dumps({"phone_number": {"country_code": "+91", "phone_number": "999999999"}})

        with app.test_client() as client:
            response = client.post(ACCOUNT_URL, headers=HEADERS, data=request_body)

            assert response.status_code == 400
            assert response.json
            assert response.json.get("code") == OTPErrorCode.REQUEST_FAILED
            assert response.json.get("message") == "Please provide a valid phone number."
            assert mock_send_sms.called is False
