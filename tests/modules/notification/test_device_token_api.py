import json
from unittest.mock import patch

import jwt
from server import app

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.config.config_service import ConfigService
from modules.notification.internals.device_token_reader import DeviceTokenReader
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams
from tests.modules.notification.base_test_notification import BaseTestNotification

API_URL = "http://127.0.0.1:8080/api/device-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestDeviceTokenApi(BaseTestNotification):
    def _create_auth_token(self, account_id: str) -> str:
        jwt_signing_key = ConfigService[str].get_value(key="accounts.token_signing_key")
        payload = {"account_id": account_id}
        return jwt.encode(payload, jwt_signing_key, algorithm="HS256")

    def _get_auth_headers(self, account_id: str) -> dict:
        token = self._create_auth_token(account_id)
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    def test_register_device_token(self) -> None:
        # Create a test account with a unique username
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name",
                last_name="last_name",
                password="password",
                username="unique_username_for_register_test",
            )
        )

        # Prepare request data
        token_data = {"token": "fcm-token-123", "device_type": "android", "app_version": "1.0.0"}

        with app.test_client() as client:
            # Make the request with authentication
            response = client.post(API_URL, headers=self._get_auth_headers(account.id), data=json.dumps(token_data))

            # Verify response
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json["token"], "fcm-token-123")
            self.assertEqual(response.json["device_type"], "android")
            self.assertEqual(response.json["app_version"], "1.0.0")

            # Verify token was stored in database with correct user ID
            stored_token = DeviceTokenReader.get_token_by_value("fcm-token-123")
            self.assertIsNotNone(stored_token)
            self.assertEqual(stored_token.user_id, account.id)

    def test_register_device_token_unauthorized(self) -> None:
        # Prepare request data
        token_data = {"token": "fcm-token-123", "device_type": "android", "app_version": "1.0.0"}

        with app.test_client() as client:
            # Make the request without authentication
            response = client.post(API_URL, headers=HEADERS, data=json.dumps(token_data))

            # Verify unauthorized response
            self.assertEqual(response.status_code, 401)

    def test_get_device_tokens(self) -> None:
        # Create a test account with a unique username
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name",
                last_name="last_name",
                password="password",
                username="unique_username_for_get_tokens_test",
            )
        )

        # Register some tokens for this user
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id=account.id, token="token1", device_type="android", app_version="1.0"
            )
        )
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="token2", device_type="ios", app_version="1.0")
        )

        with app.test_client() as client:
            # Make the request with authentication
            response = client.get(API_URL, headers=self._get_auth_headers(account.id))

            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertIn("tokens", response.json)
            self.assertEqual(len(response.json["tokens"]), 2)
            self.assertIn("token1", response.json["tokens"])
            self.assertIn("token2", response.json["tokens"])

    def test_get_device_tokens_unauthorized(self) -> None:
        with app.test_client() as client:
            # Make the request without authentication
            response = client.get(API_URL, headers=HEADERS)

            # Verify unauthorized response
            self.assertEqual(response.status_code, 401)

    def test_delete_device_token(self) -> None:
        # Create a test account with a unique username
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name",
                last_name="last_name",
                password="password",
                username="unique_username_for_delete_token_test",
            )
        )

        # Register a token
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id=account.id, token="token-to-delete", device_type="android", app_version="1.0"
            )
        )

        # Verify token exists
        self.assertIsNotNone(DeviceTokenReader.get_token_by_value("token-to-delete"))

        with app.test_client() as client:
            # Make the delete request
            response = client.delete(
                API_URL, headers=self._get_auth_headers(account.id), data=json.dumps({"token": "token-to-delete"})
            )

            # Verify response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["message"], "Device token removed successfully")

            # Verify token was removed
            self.assertIsNone(DeviceTokenReader.get_token_by_value("token-to-delete"))

    def test_delete_nonexistent_token(self) -> None:
        # Create a test account with a unique username
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name",
                last_name="last_name",
                password="password",
                username="unique_username_for_nonexistent_token_test",
            )
        )

        with app.test_client() as client:
            # Make the delete request for a nonexistent token
            response = client.delete(
                API_URL, headers=self._get_auth_headers(account.id), data=json.dumps({"token": "nonexistent-token"})
            )

            # Verify response
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json["message"], "Device token not found")

    def test_delete_device_token_missing_token(self) -> None:
        # Create a test account
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        with app.test_client() as client:
            # Make the delete request without specifying a token
            response = client.delete(API_URL, headers=self._get_auth_headers(account.id), data=json.dumps({}))

            # Verify response
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["message"], "Token is required")

    def test_delete_device_token_unauthorized(self) -> None:
        with app.test_client() as client:
            # Make the delete request without authentication
            response = client.delete(API_URL, headers=HEADERS, data=json.dumps({"token": "token-to-delete"}))

            # Verify unauthorized response
            self.assertEqual(response.status_code, 401)
