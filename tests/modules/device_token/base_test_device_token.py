# tests/modules/device_token/base_test_device_token.py
import json
import unittest
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

from server import app
from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, Account
from modules.logger.logger_manager import LoggerManager
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository
from modules.device_token.rest_api.device_token_rest_api_server import DeviceTokenRestApiServer
from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.types import DeviceToken, CreateDeviceTokenParams, Platform


class BaseTestDeviceToken(unittest.TestCase):
    """Base test class for device token testing with common utilities"""
    
    ACCESS_TOKEN_URL = "/api/access-tokens"
    DEVICE_TOKEN_URL_TEMPLATE = "/api/accounts/{account_id}/devices"
    HEADERS = {"Content-Type": "application/json"}

    DEFAULT_DEVICE_TOKEN = "fcm_test_token_123"
    DEFAULT_PLATFORM = Platform.ANDROID
    DEFAULT_DEVICE_INFO = {"app_version": "1.0.0"}
    DEFAULT_USERNAME = "test@example.com"
    DEFAULT_PASSWORD = "password"

    def setUp(self) -> None:
        """Set up test environment before each test"""
        LoggerManager.mount_logger()
        DeviceTokenRestApiServer.create()

    def tearDown(self) -> None:
        """Clean up test data after each test"""
        DeviceTokenRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})

    def create_test_account(self, username: Optional[str] = None) -> Account:
        """
        Create a test account with optional custom username
        
        Args:
            username: Optional custom username, defaults to DEFAULT_USERNAME
            
        Returns:
            Created Account object
        """
        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                username=username or self.DEFAULT_USERNAME,
                password=self.DEFAULT_PASSWORD,
                first_name="Test",
                last_name="User",
            )
        )

    def get_access_token(self, username: str) -> str:
        """
        Get access token for a user
        
        Args:
            username: Username to authenticate with
            
        Returns:
            Access token string
        """
        with app.test_client() as client:
            response = client.post(
                self.ACCESS_TOKEN_URL,
                headers=self.HEADERS,
                data=json.dumps(
                    {"username": username, "password": self.DEFAULT_PASSWORD}
                ),
            )
            return response.json["token"]

    def create_account_and_get_token(self, username: Optional[str] = None) -> Tuple[Account, str]:
        """
        Create account and get access token in one call
        
        Args:
            username: Optional custom username
            
        Returns:
            Tuple of (Account, access_token)
        """
        account = self.create_test_account(username=username)
        token = self.get_access_token(account.username)
        return account, token

    def create_test_device_token(
        self, 
        account_id: str, 
        token: Optional[str] = None,
        platform: Optional[Platform] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> DeviceToken:
        """
        Create a test device token with optional custom parameters
        
        Args:
            account_id: Account ID to associate device with
            token: Optional custom device token string
            platform: Optional platform (defaults to DEFAULT_PLATFORM)
            device_info: Optional device info dict (defaults to DEFAULT_DEVICE_INFO)
            
        Returns:
            Created DeviceToken object
        """
        params = CreateDeviceTokenParams(
            account_id=account_id,
            device_token=token or self.DEFAULT_DEVICE_TOKEN,
            platform=platform or self.DEFAULT_PLATFORM,
            device_info=device_info if device_info is not None else self.DEFAULT_DEVICE_INFO,
        )
        return DeviceTokenService.create_device_token(params=params)

    def make_authenticated_request(
        self,
        method: str,
        account_id: str,
        token: str,
        device_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Make an authenticated HTTP request to device token endpoints
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            account_id: Account ID for URL construction
            token: Bearer token for authentication
            device_id: Optional device ID for URL construction
            data: Optional request body data
            
        Returns:
            Flask response object
        """
        url = self.DEVICE_TOKEN_URL_TEMPLATE.format(account_id=account_id)
        if device_id:
            url += f"/{device_id}"

        headers = {**self.HEADERS, "Authorization": f"Bearer {token}"}

        with app.test_client() as client:
            if method == "GET":
                return client.get(url, headers=headers)
            elif method == "POST":
                return client.post(url, headers=headers, data=json.dumps(data))
            elif method == "PATCH":
                return client.patch(url, headers=headers, data=json.dumps(data))
            elif method == "DELETE":
                return client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

    def make_unauthenticated_request(
        self,
        method: str,
        account_id: str,
        device_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Make an unauthenticated HTTP request to device token endpoints
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            account_id: Account ID for URL construction
            device_id: Optional device ID for URL construction
            data: Optional request body data
            
        Returns:
            Flask response object
        """
        url = self.DEVICE_TOKEN_URL_TEMPLATE.format(account_id=account_id)
        if device_id:
            url += f"/{device_id}"

        with app.test_client() as client:
            if method == "GET":
                return client.get(url, headers=self.HEADERS)
            elif method == "POST":
                return client.post(url, headers=self.HEADERS, data=json.dumps(data))
            elif method == "PATCH":
                return client.patch(url, headers=self.HEADERS, data=json.dumps(data))
            elif method == "DELETE":
                return client.delete(url, headers=self.HEADERS)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

    def assert_device_token_response(
        self,
        response_data: Dict[str, Any],
        expected_token: Optional[str] = None,
        expected_platform: Optional[str] = None,
        expected_active: bool = True
    ):
        """
        Helper to assert device token response structure and values
        
        Args:
            response_data: Response JSON data
            expected_token: Expected device token string
            expected_platform: Expected platform value
            expected_active: Expected active status
        """
        assert "id" in response_data
        assert "device_token" in response_data
        assert "platform" in response_data
        assert "active" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
        
        if expected_token:
            assert response_data["device_token"] == expected_token
        if expected_platform:
            assert response_data["platform"] == expected_platform
        assert response_data["active"] == expected_active
