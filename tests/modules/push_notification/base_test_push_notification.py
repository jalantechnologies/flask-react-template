# tests/modules/push_notification/base_test_push_notification.py
import unittest
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from server import app
from modules.account.account_service import AccountService
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import CreateAccountByUsernameAndPasswordParams, Account
from modules.logger.logger_manager import LoggerManager
from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository
from modules.device_token.types import CreateDeviceTokenParams, DeviceToken, Platform
from modules.push_notification.internal.store.push_notification_repository import PushNotificationRepository
from modules.push_notification.push_notification_service import PushNotificationService
from modules.push_notification.fcm_service import FCMService
from modules.push_notification.types import (
    PushNotification,
    CreatePushNotificationParams,
    Priority,
    NotificationStatus,
    SendPushNotificationParams,
)
from modules.logger.logger import Logger


class BaseTestPushNotification(unittest.TestCase):
    """Base test class for push notification testing with common utilities"""
    
    DEFAULT_USERNAME = "test@example.com"
    DEFAULT_PASSWORD = "password"
    DEFAULT_DEVICE_TOKEN = "fcm_test_token_123"
    DEFAULT_PLATFORM = Platform.ANDROID
    DEFAULT_TITLE = "Test Notification"
    DEFAULT_BODY = "This is a test notification"
    DEFAULT_DATA = {"type": "test", "id": "123"}

    def setUp(self) -> None:
        """Set up test environment before each test"""
        LoggerManager.mount_logger()
        
        # Mock FCM Service to avoid actual Firebase calls
        FCMService._initialized = True
        
        # Patch logger methods to avoid spam
        self.logger_info_patcher = patch.object(Logger, "info")
        self.logger_error_patcher = patch.object(Logger, "error")
        self.logger_warn_patcher = patch.object(Logger, "warn")
        
        self.mock_logger_info = self.logger_info_patcher.start()
        self.mock_logger_error = self.logger_error_patcher.start()
        self.mock_logger_warn = self.logger_warn_patcher.start()

    def tearDown(self) -> None:
        """Clean up test data after each test"""
        PushNotificationRepository.collection().delete_many({})
        DeviceTokenRepository.collection().delete_many({})
        AccountRepository.collection().delete_many({})
        
        # Stop logger patches
        self.logger_info_patcher.stop()
        self.logger_error_patcher.stop()
        self.logger_warn_patcher.stop()
        
        # Reset FCM state
        FCMService._initialized = False

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

    def create_test_device_token(
        self, 
        account_id: str, 
        token: Optional[str] = None,
        platform: Optional[Platform] = None,
    ) -> DeviceToken:
        """
        Create a test device token with optional custom parameters
        
        Args:
            account_id: Account ID to associate device with
            token: Optional custom device token string
            platform: Optional platform (defaults to DEFAULT_PLATFORM)
            
        Returns:
            Created DeviceToken object
        """
        params = CreateDeviceTokenParams(
            account_id=account_id,
            device_token=token or self.DEFAULT_DEVICE_TOKEN,
            platform=platform or self.DEFAULT_PLATFORM,
            device_info={"app_version": "1.0.0"},
        )
        return DeviceTokenService.create_device_token(params=params)

    def create_mock_fcm_response(
        self,
        success: bool = True,
        message_id: Optional[str] = "msg_123",
        error: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        """
        Create a mock FCM response object
        
        Args:
            success: Whether the response was successful
            message_id: Optional message ID
            error: Optional error message
            error_code: Optional error code
            
        Returns:
            Mock FCM response object
        """
        from modules.push_notification.types import FCMResponse
        
        return FCMResponse(
            success=success,
            message_id=message_id,
            error=error,
            error_code=error_code,
        )

    def create_mock_fcm_batch_response(
        self,
        success_count: int = 1,
        failure_count: int = 0,
        responses: Optional[list] = None,
    ):
        """
        Create a mock FCM batch response object
        
        Args:
            success_count: Number of successful sends
            failure_count: Number of failed sends
            responses: Optional list of individual responses
            
        Returns:
            Mock FCM batch response object
        """
        from modules.push_notification.types import FCMBatchResponse
        
        if responses is None:
            responses = []
            for _ in range(success_count):
                responses.append(self.create_mock_fcm_response(success=True))
            for _ in range(failure_count):
                responses.append(self.create_mock_fcm_response(success=False, error="Failed"))
        
        return FCMBatchResponse(
            success_count=success_count,
            failure_count=failure_count,
            responses=responses,
        )

    def assert_notification_fields(
        self,
        notification: PushNotification,
        expected_title: Optional[str] = None,
        expected_body: Optional[str] = None,
        expected_status: Optional[NotificationStatus] = None,
        expected_priority: Optional[Priority] = None,
        expected_account_id: Optional[str] = None,
    ):
        """
        Helper to assert notification fields
        
        Args:
            notification: PushNotification object to check
            expected_title: Expected title
            expected_body: Expected body
            expected_status: Expected status
            expected_priority: Expected priority
            expected_account_id: Expected account ID
        """
        assert notification is not None
        assert notification.id is not None
        assert notification.created_at is not None
        assert notification.updated_at is not None
        
        if expected_title:
            assert notification.title == expected_title
        if expected_body:
            assert notification.body == expected_body
        if expected_status:
            assert notification.status == expected_status
        if expected_priority:
            assert notification.priority == expected_priority
        if expected_account_id:
            assert notification.account_id == expected_account_id

    def create_send_push_params(
        self,
        title: Optional[str] = None,
        body: Optional[str] = None,
        data: Optional[dict] = None,
        priority: str = "normal",
    ) -> SendPushNotificationParams:
        """
        Create SendPushNotificationParams with defaults
        
        Args:
            title: Notification title
            body: Notification body
            data: Optional data payload
            priority: Priority level
            
        Returns:
            SendPushNotificationParams object
        """
        return SendPushNotificationParams(
            title=title or self.DEFAULT_TITLE,
            body=body or self.DEFAULT_BODY,
            data=data or self.DEFAULT_DATA,
            priority=priority,
        )
