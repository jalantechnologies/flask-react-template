import json

from server import app

from modules.account.account_service import AccountService
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import (
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from tests.conftest import TEST_ACTOR
from tests.modules.authentication.base_test_access_token import BaseTestAccessToken

ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"
HEADERS = {"Content-Type": "application/json"}


class TestAuthenticationService(BaseTestAccessToken):
    def test_get_access_token_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )

        assert response.status_code == 201
        assert response.json is not None
        assert response.json.get("account_id") == account.id
        assert response.json.get("token")
        assert response.json.get("expires_at")

    def test_verify_access_token_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            token_response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )
            assert token_response.json is not None
            token = token_response.json.get("token")

            authenticated_response = client.get(
                f"{ACCOUNT_URL}/{account.id}", headers={"Authorization": f"Bearer {token}"}
            )

        assert authenticated_response.status_code == 200
        assert authenticated_response.json is not None
        assert authenticated_response.json.get("id") == account.id

    def test_get_access_token_by_phone_number(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
        )

        with app.test_client() as client:
            response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"phone_number": phone_number, "otp_code": otp.otp_code}),
            )

        assert response.status_code == 201
        assert response.json is not None
        assert response.json.get("account_id") == account.id
        assert response.json.get("token")
        assert response.json.get("expires_at")

    def test_verify_access_token_by_phone_number(self) -> None:
        phone_number = {"country_code": "+91", "phone_number": "9999999999"}
        account = AccountWriter.create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=PhoneNumber(**phone_number)), actor=TEST_ACTOR
        )
        otp = AuthenticationService.create_otp(
            params=CreateOTPParams(phone_number=PhoneNumber(**phone_number)), account_id=account.id, actor=TEST_ACTOR
        )

        with app.test_client() as client:
            token_response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"phone_number": phone_number, "otp_code": otp.otp_code}),
            )
            assert token_response.json is not None
            token = token_response.json.get("token")

            authenticated_response = client.get(
                f"{ACCOUNT_URL}/{account.id}", headers={"Authorization": f"Bearer {token}"}
            )

        assert authenticated_response.status_code == 200
        assert authenticated_response.json is not None
        assert authenticated_response.json.get("id") == account.id
