import json

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
    def _create_test_account_and_get_token(self):
        """Helper method to create test account and get access token"""
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password", username="testuser@example.com"
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
        """Test successful device token registration"""
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

    def test_register_device_token_upsert_existing(self) -> None:
        """Test upserting an existing device token updates user_id and device_type"""
        account1, token1 = self._create_test_account_and_get_token()
        account2 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test2", last_name="User2", password="password", username="testuser2@example.com"
            )
        )

        with app.test_client() as client:
            # Get token for second account
            response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": account2.username, "password": "password"}),
            )
            token2 = response.json.get("token")

        device_token_data = {"token": "fcm_token_123", "device_type": "android"}

        with app.test_client() as client:
            # Register token with first account
            response1 = client.post(
                DEVICE_TOKEN_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token1}"},
                data=json.dumps(device_token_data),
            )
            assert response1.status_code == 201
            assert response1.json.get("user_id") == account1.id

            # Register same token with second account (should update)
            device_token_data["device_type"] = "ios"
            response2 = client.post(
                DEVICE_TOKEN_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token2}"},
                data=json.dumps(device_token_data),
            )
            assert response2.status_code == 201
            assert response2.json.get("user_id") == account2.id
            assert response2.json.get("device_type") == "ios"

    def test_register_device_token_without_auth(self) -> None:
        """Test device token registration without authentication"""
        device_token_data = {"token": "fcm_token_123", "device_type": "android"}

        with app.test_client() as client:
            response = client.post(DEVICE_TOKEN_URL, headers=HEADERS, data=json.dumps(device_token_data))

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_get_user_device_tokens_success(self) -> None:
        """Test getting user's device tokens"""
        account, token = self._create_test_account_and_get_token()

        # Register multiple tokens for the user
        tokens_to_register = ["fcm_token_1", "fcm_token_2", "fcm_token_3"]
        for fcm_token in tokens_to_register:
            NotificationService.upsert_device_token(
                params=RegisterDeviceTokenParams(user_id=account.id, token=fcm_token, device_type="android")
            )

        with app.test_client() as client:
            response = client.get(DEVICE_TOKEN_URL, headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == 200
            assert response.json
            assert "tokens" in response.json
            returned_tokens = response.json.get("tokens")
            assert len(returned_tokens) == 3
            assert all(token in returned_tokens for token in tokens_to_register)

    def test_get_user_device_tokens_empty(self) -> None:
        """Test getting device tokens when user has none"""
        account, token = self._create_test_account_and_get_token()

        with app.test_client() as client:
            response = client.get(DEVICE_TOKEN_URL, headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == 200
            assert response.json
            assert response.json.get("tokens") == []

    def test_get_user_device_tokens_without_auth(self) -> None:
        """Test getting device tokens without authentication"""
        with app.test_client() as client:
            response = client.get(DEVICE_TOKEN_URL)

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_delete_device_token_success(self) -> None:
        """Test successful device token deletion"""
        account, token = self._create_test_account_and_get_token()

        # Register a token first
        device_token = NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm_token_to_delete", device_type="android")
        )

        delete_data = {"token": "fcm_token_to_delete"}

        with app.test_client() as client:
            response = client.delete(
                DEVICE_TOKEN_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data=json.dumps(delete_data)
            )

            assert response.status_code == 200
            assert response.json
            assert response.json.get("message") == "Device token removed successfully"

    def test_delete_device_token_not_found(self) -> None:
        """Test deleting a non-existent device token"""
        account, token = self._create_test_account_and_get_token()

        delete_data = {"token": "non_existent_token"}

        with app.test_client() as client:
            response = client.delete(
                DEVICE_TOKEN_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data=json.dumps(delete_data)
            )

            assert response.status_code == 404
            assert response.json
            assert response.json.get("message") == "Device token not found"

    def test_delete_device_token_missing_token_param(self) -> None:
        """Test deleting device token without providing token parameter"""
        account, token = self._create_test_account_and_get_token()

        delete_data = {}  # Missing token parameter

        with app.test_client() as client:
            response = client.delete(
                DEVICE_TOKEN_URL, headers={**HEADERS, "Authorization": f"Bearer {token}"}, data=json.dumps(delete_data)
            )

            assert response.status_code == 400
            assert response.json
            assert response.json.get("message") == "Token is required"

    def test_delete_device_token_without_auth(self) -> None:
        """Test deleting device token without authentication"""
        delete_data = {"token": "some_token"}

        with app.test_client() as client:
            response = client.delete(DEVICE_TOKEN_URL, headers=HEADERS, data=json.dumps(delete_data))

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND
