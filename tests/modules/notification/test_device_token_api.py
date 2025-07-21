import json
import uuid

from server import app

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams
from tests.modules.notification.base_test_notification import BaseTestNotification

DEVICE_TOKEN_URL = "http://127.0.0.1:8080/api/device-tokens"
ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestDeviceTokenApi(BaseTestNotification):
    def _create_test_account_and_get_token(self, username_suffix=""):

        unique_id = str(uuid.uuid4())[:8]
        username = f"testuser{username_suffix}_{unique_id}@example.com"

        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password", username=username
            )
        )

        with app.test_client() as client:
            response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )
            return account, response.json.get("token")

    def test_register_device_token_success(self) -> None:
        account, token = self._create_test_account_and_get_token()

        device_token_data = {"token": "fcm_token_123", "device_type": "android"}

        with app.test_client() as client:
            response = client.post(
                DEVICE_TOKEN_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(device_token_data),
            )

            assert response.status_code == 201
            assert response.json
            assert response.json.get("token") == "fcm_token_123"
            assert response.json.get("device_type") == "android"
            assert response.json.get("user_id") == account.id
            assert "id" in response.json
            assert "created_at" in response.json
            assert "updated_at" in response.json

    def test_register_device_token_without_auth(self) -> None:
        device_token_data = {"token": "fcm_token_123", "device_type": "android"}

        with app.test_client() as client:
            response = client.post(DEVICE_TOKEN_URL, headers=HEADERS, data=json.dumps(device_token_data))

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND
