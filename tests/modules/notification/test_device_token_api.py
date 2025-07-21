import json
from unittest import mock

from server import app

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.authentication_service import AuthenticationService
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams
from tests.modules.notification.base_test_notification import BaseTestNotification

DEVICE_TOKEN_URL = "http://127.0.0.1:8080/api/device-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestDeviceTokenApi(BaseTestNotification):
    def test_create_device_token(self) -> None:
        # Create an account and get an access token
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)

        # Create a device token using the API
        token_data = {"token": "fcm-token-123", "device_type": "android"}

        with app.test_client() as client:
            response = client.post(
                DEVICE_TOKEN_URL,
                headers={"Authorization": f"Bearer {access_token.token}", "Content-Type": "application/json"},
                data=json.dumps(token_data),
            )

            self.assertEqual(response.status_code, 201)
            self.assertIn("id", response.json)
            self.assertEqual(response.json["token"], "fcm-token-123")
            self.assertEqual(response.json["device_type"], "android")
            self.assertEqual(response.json["user_id"], account.id)

    def test_get_user_device_tokens(self) -> None:
        # Create an account and get an access token
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)

        # Create some device tokens for the account
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-1", device_type="android")
        )
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-2", device_type="ios")
        )

        # Get the device tokens using the API
        with app.test_client() as client:
            response = client.get(DEVICE_TOKEN_URL, headers={"Authorization": f"Bearer {access_token.token}"})

            self.assertEqual(response.status_code, 200)
            self.assertIn("tokens", response.json)
            self.assertEqual(len(response.json["tokens"]), 2)
            self.assertIn("fcm-token-1", response.json["tokens"])
            self.assertIn("fcm-token-2", response.json["tokens"])

    def test_delete_device_token(self) -> None:
        # Create an account and get an access token
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)

        # Create a device token
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-123", device_type="android")
        )

        # Delete the device token using the API
        with app.test_client() as client:
            response = client.delete(
                DEVICE_TOKEN_URL,
                headers={"Authorization": f"Bearer {access_token.token}", "Content-Type": "application/json"},
                data=json.dumps({"token": "fcm-token-123"}),
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["message"], "Device token removed successfully")

            # Verify that the token was removed
            get_response = client.get(DEVICE_TOKEN_URL, headers={"Authorization": f"Bearer {access_token.token}"})

            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(len(get_response.json["tokens"]), 0)

    def test_delete_nonexistent_device_token(self) -> None:
        # Create an account and get an access token
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)

        # Try to delete a nonexistent device token
        with app.test_client() as client:
            response = client.delete(
                DEVICE_TOKEN_URL,
                headers={"Authorization": f"Bearer {access_token.token}", "Content-Type": "application/json"},
                data=json.dumps({"token": "nonexistent-token"}),
            )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json["message"], "Device token not found")

    def test_delete_device_token_missing_token(self) -> None:
        # Create an account and get an access token
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)

        # Try to delete a device token without providing a token
        with app.test_client() as client:
            response = client.delete(
                DEVICE_TOKEN_URL,
                headers={"Authorization": f"Bearer {access_token.token}", "Content-Type": "application/json"},
                data=json.dumps({}),
            )

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["message"], "Token is required")

    def test_unauthorized_access(self) -> None:
        # Try to access the API without authorization
        with app.test_client() as client:
            response = client.get(DEVICE_TOKEN_URL)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json["code"], "ACCESS_TOKEN_ERR_03")
