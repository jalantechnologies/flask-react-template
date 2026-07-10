from datetime import datetime, timedelta

import jwt
from server import app

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from modules.config.config_service import ConfigService
from tests.modules.account.base_test_account import BaseTestAccount

ACCOUNT_URL = "http://127.0.0.1:8080/api/accounts"


class TestAccountGetApi(BaseTestAccount):
    def test_given_authenticated_account_when_requesting_own_account_then_returns_account_details(self) -> None:
        with app.test_client() as client:
            response = client.get(
                f"{ACCOUNT_URL}/{self.account.id}", headers={"Authorization": f"Bearer {self.access_token.token}"}
            )

            assert response.status_code == 200
            assert response.json
            assert response.json.get("id") == self.account.id
            assert response.json.get("username") == self.account.username
            assert response.json.get("first_name") == self.account.first_name
            assert response.json.get("last_name") == self.account.last_name

    def test_given_no_authorization_header_when_requesting_account_then_returns_unauthorized(self) -> None:
        with app.test_client() as client:
            response = client.get(f"{ACCOUNT_URL}/{self.account.id}")

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_given_invalid_access_token_when_requesting_account_then_returns_unauthorized(self) -> None:
        with app.test_client() as client:
            response = client.get(f"{ACCOUNT_URL}/{self.account.id}", headers={"Authorization": "Bearer invalid_token"})

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_given_expired_access_token_when_requesting_account_then_returns_unauthorized(self) -> None:
        jwt_signing_key = ConfigService[str].get_value(key="accounts.token_signing_key")
        jwt_expiry = timedelta(days=ConfigService[int].get_value(key="accounts.token_expiry_days") - 1)
        expired_payload = {"account_id": self.account.id, "exp": (datetime.now() - jwt_expiry).timestamp()}
        expired_token = jwt.encode(expired_payload, jwt_signing_key, algorithm="HS256")

        with app.test_client() as client:
            response = client.get(
                f"{ACCOUNT_URL}/{self.account.id}", headers={"Authorization": f"Bearer {expired_token}"}
            )

            assert response.status_code == 401
            assert "Access token has expired. Please login again." in response.json.get("message", "")
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_EXPIRED

    def test_given_authenticated_account_when_requesting_another_users_account_then_returns_unauthorized(self) -> None:
        other_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="other_first_name", last_name="other_last_name", password="password", username="other_user"
            )
        )

        with app.test_client() as client:
            response = client.get(
                f"{ACCOUNT_URL}/{other_account.id}", headers={"Authorization": f"Bearer {self.access_token.token}"}
            )

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.UNAUTHORIZED_ACCESS
