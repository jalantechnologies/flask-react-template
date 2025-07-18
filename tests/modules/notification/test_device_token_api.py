import json
from unittest.mock import patch
import asyncio
import time

import jwt
from temporalio.client import WorkflowExecutionStatus
from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.config.config_service import ConfigService
from modules.application.application_service import ApplicationService
from modules.notification.workers.token_cleanup_worker import TokenCleanupWorker
from server import app

from tests.modules.notification.base_test_notification import BaseTestNotification


class TestDeviceTokenApi(BaseTestNotification):
    def setUp(self) -> None:
        self.account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        jwt_signing_key = ConfigService[str].get_value(key="accounts.token_signing_key")
        payload = {"account_id": self.account.id}
        self.access_token = jwt.encode(payload, jwt_signing_key, algorithm="HS256")

        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.access_token}"}
        self.device_token_url = "http://127.0.0.1:8080/api/device-tokens"

    def test_register_device_token(self) -> None:
        token_data = {"token": "fcm-token-123", "device_type": "android", "app_version": "1.0.0"}

        with app.test_client() as client:
            response = client.post(self.device_token_url, headers=self.headers, data=json.dumps(token_data))

        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.json)
        self.assertEqual(response.json["token"], token_data["token"])
        self.assertEqual(response.json["device_type"], token_data["device_type"])
        self.assertEqual(response.json["app_version"], token_data["app_version"])

    def test_register_device_token_missing_auth(self) -> None:
        token_data = {"token": "fcm-token-123", "device_type": "android", "app_version": "1.0.0"}
        headers_without_auth = {"Content-Type": "application/json"}

        with app.test_client() as client:
            response = client.post(self.device_token_url, headers=headers_without_auth, data=json.dumps(token_data))

        self.assertEqual(response.status_code, 401)

    def test_get_device_tokens(self) -> None:
        token_data = {"token": "fcm-token-123", "device_type": "android", "app_version": "1.0.0"}

        with app.test_client() as client:
            client.post(self.device_token_url, headers=self.headers, data=json.dumps(token_data))

        with app.test_client() as client:
            response = client.get(self.device_token_url, headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn("tokens", response.json)
        self.assertEqual(len(response.json["tokens"]), 1)
        self.assertEqual(response.json["tokens"][0], token_data["token"])

    def test_delete_device_token(self) -> None:
        token_data = {"token": "fcm-token-123", "device_type": "android", "app_version": "1.0.0"}

        with app.test_client() as client:
            client.post(self.device_token_url, headers=self.headers, data=json.dumps(token_data))

        with app.test_client() as client:
            response = client.delete(
                self.device_token_url, headers=self.headers, data=json.dumps({"token": token_data["token"]})
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Device token removed successfully")

        with app.test_client() as client:
            get_response = client.get(self.device_token_url, headers=self.headers)
        self.assertEqual(len(get_response.json["tokens"]), 0)

    def test_delete_nonexistent_token(self) -> None:
        with app.test_client() as client:
            response = client.delete(
                self.device_token_url, headers=self.headers, data=json.dumps({"token": "nonexistent-token"})
            )

        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Device token not found")

    def test_delete_missing_token_param(self) -> None:
        with app.test_client() as client:
            response = client.delete(self.device_token_url, headers=self.headers, data=json.dumps({}))

        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Token is required")

    @patch("modules.notification.notification_service.NotificationService.cleanup_inactive_tokens")
    def test_token_cleanup_worker_execution(self, mock_cleanup_tokens) -> None:
        """Test the worker's business logic directly"""
        mock_cleanup_tokens.return_value = 5

        asyncio.run(TokenCleanupWorker.execute())

        mock_cleanup_tokens.assert_called_once()
        mock_cleanup_tokens.assert_called_with(days=60)

    def test_token_cleanup_worker_temporal_integration(self) -> None:
        worker_id = ApplicationService.run_worker_immediately(cls=TokenCleanupWorker)

        self.assertIsNotNone(worker_id)

        time.sleep(2)

        worker = ApplicationService.get_worker_by_id(worker_id=worker_id)
        self.assertEqual(worker.status, WorkflowExecutionStatus.COMPLETED)
