import json
import unittest
from typing import Tuple
from datetime import datetime

from server import app
from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, Account
from modules.logger.logger_manager import LoggerManager
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository
from modules.device_token.rest_api.device_token_rest_api_server import DeviceTokenRestApiServer
from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.types import DeviceToken


class BaseTestDeviceToken(unittest.TestCase):
    ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
    DEVICE_TOKEN_URL_TEMPLATE = "http://127.0.0.1:8080/api/accounts/{account_id}/devices"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_DEVICE_TOKEN = "fcm_test_token_123456789"
    DEFAULT_PLATFORM = "android"
    DEFAULT_DEVICE_INFO = {"app_version": "1.0.0", "os_version": "13.0", "device_model": "Pixel 5"}
    DEFAULT_USERNAME = "testuser@example.com"
    DEFAULT_PASSWORD = "testpassword"
    DEFAULT_FIRST_NAME = "Test"
    DEFAULT_LAST_NAME = "User"

    def setUp(self) -> None:
        LoggerManager.mount_logger()
        DeviceTokenRestApiServer.create()

    def tearDown(self) -> None:
        """Clean up test data after each test - delete all device tokens and accounts"""
        DeviceTokenRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    # ACCOUNT AND TOKEN HELPER METHODS

    def create_test_account(
        self, username: str = None, password: str = None, first_name: str = None, last_name: str = None
    ) -> Account:
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=username or self.DEFAULT_USERNAME,
                password=password or self.DEFAULT_PASSWORD,
                first_name=first_name or self.DEFAULT_FIRST_NAME,
                last_name=last_name or self.DEFAULT_LAST_NAME,
            )
        )

    def get_access_token(self, username: str = None, password: str = None) -> str:
        with app.test_client() as client:
            response = client.post(
                self.ACCESS_TOKEN_URL,
                headers=self.HEADERS,
                data=json.dumps(
                    {"username": username or self.DEFAULT_USERNAME, "password": password or self.DEFAULT_PASSWORD}
                ),
            )
            return response.json.get("token")

    def create_account_and_get_token(self, username: str = None, password: str = None) -> Tuple[Account, str]:
        test_username = username or f"testuser_{id(self)}@example.com"
        test_password = password or self.DEFAULT_PASSWORD

        account = self.create_test_account(username=test_username, password=test_password)
        token = self.get_access_token(username=test_username, password=test_password)
        return account, token

    # DEVICE TOKEN HELPER METHODS

    def create_test_device_token(
        self,
        account_id: str,
        device_token: str = None,
        platform: str = None,
        device_info: dict = None,
    ) -> DeviceToken:
        return DeviceTokenService.register_device_token(
            account_id=account_id,
            device_token=device_token or self.DEFAULT_DEVICE_TOKEN,
            platform=platform or self.DEFAULT_PLATFORM,
            device_info=device_info or self.DEFAULT_DEVICE_INFO,
        )

    def create_multiple_test_tokens(
        self, account_id: str, count: int, platform: str = None
    ) -> list[DeviceToken]:
        tokens = []
        for i in range(count):
            token = DeviceTokenService.register_device_token(
                account_id=account_id,
                device_token=f"token_{platform or self.DEFAULT_PLATFORM}_{i}",
                platform=platform or self.DEFAULT_PLATFORM,
                device_info={"device_model": f"Device {i}"},
            )
            tokens.append(token)
        return tokens

    # HTTP REQUEST HELPER METHODS

    def make_authenticated_request(
        self,
        method: str,
        account_id: str,
        token: str,
        device_token_id: str = None,
        data: dict = None,
    ):
        url = self.DEVICE_TOKEN_URL_TEMPLATE.format(account_id=account_id)
        if device_token_id:
            url = f"{url}/{device_token_id}"

        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers=headers)
            elif method.upper() == "POST":
                return client.post(url, headers=headers, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers=headers)

    def make_unauthenticated_request(self, method: str, account_id: str = "dummy_account", device_token_id: str = None, data: dict = None):
        url = self.DEVICE_TOKEN_URL_TEMPLATE.format(account_id=account_id)
        if device_token_id:
            url = f"{url}/{device_token_id}"

        with app.test_client() as client:
            if method.upper() == "GET":
                return client.get(url, headers=self.HEADERS)
            elif method.upper() == "POST":
                return client.post(url, headers=self.HEADERS, data=json.dumps(data) if data is not None else None)
            elif method.upper() == "DELETE":
                return client.delete(url, headers=self.HEADERS)

    # ASSERTION HELPER METHODS

    def assert_device_token_response(self, response_json: dict, expected_token: DeviceToken = None, **expected_fields):
        assert response_json.get("id") is not None, "Missing id field"
        assert response_json.get("account_id") is not None, "Missing account_id field"
        assert response_json.get("device_token") is not None, "Missing device_token field"
        assert response_json.get("platform") is not None, "Missing platform field"
        assert "active" in response_json, "Missing active field"
        assert response_json.get("created_at") is not None, "Missing created_at field"
        assert response_json.get("updated_at") is not None, "Missing updated_at field"

        if expected_token:
            assert response_json.get("id") == expected_token.id
            assert response_json.get("account_id") == expected_token.account_id
            assert response_json.get("device_token") == expected_token.device_token
            assert response_json.get("platform") == expected_token.platform

        for field, value in expected_fields.items():
            assert response_json.get(field) == value

    def assert_error_response(self, response, expected_status: int, expected_error_code: str):
        assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"
        assert response.json is not None, f"Expected JSON response, got None"
        assert (
            response.json.get("code") == expected_error_code
        ), f"Expected error code {expected_error_code}, got {response.json.get('code')}"

    def insert_raw_device_token(
        self,
        *,
        account_id: str,
        device_token: str,
        platform: str,
        active: bool = True,
        created_at: datetime | None = None,
        last_used_at: datetime | None = None,
    ):
        from modules.device_token.internal.store.device_token_repository import (
            DeviceTokenRepository,
        )
        from bson import ObjectId
        from datetime import datetime

        now = datetime.now()

        doc = {
            "_id": ObjectId(),
            "account_id": account_id,
            "device_token": device_token,
            "platform": platform,
            "active": active,
            "created_at": created_at or now,
            "updated_at": now,
            "last_used_at": last_used_at,
        }

        DeviceTokenRepository.collection().insert_one(doc)
        return doc