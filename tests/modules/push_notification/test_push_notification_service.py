# tests/modules/push_notification/test_push_notification_service.py
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from modules.push_notification.push_notification_service import PushNotificationService
from modules.push_notification.errors import InvalidTokenError, InvalidPriorityError
from modules.push_notification.types import (
    NotificationStatus,
    Priority,
    NotificationResult,
)
from modules.device_token.types import GetDeviceTokensParams
from tests.modules.push_notification.base_test_push_notification import BaseTestPushNotification


class TestPushNotificationService(BaseTestPushNotification):
    """Comprehensive tests for Push Notification Service"""

    def setUp(self) -> None:
        super().setUp()
        self.account = self.create_test_account()

    # -------------------------
    # SEND NOTIFICATION
    # -------------------------

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_notification_normal_priority(self, mock_fcm_send):
        """Test sending notification with normal priority (queued)"""
        device_token = self.create_test_device_token(self.account.id, "token_1")

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Test Title",
            body="Test Body",
            priority="normal"
        )

        assert notification is not None
        assert notification.title == "Test Title"
        assert notification.body == "Test Body"
        assert notification.status == NotificationStatus.PENDING
        assert notification.priority == Priority.NORMAL
        assert notification.account_id == self.account.id
        assert device_token.id in notification.device_token_ids

        # Normal priority should NOT call FCM immediately
        mock_fcm_send.assert_not_called()

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_notification_immediate_priority(self, mock_fcm_send):
        """Test sending notification with immediate priority (synchronous)"""
        device_token = self.create_test_device_token(self.account.id, "token_1")
        mock_fcm_send.return_value = self.create_mock_fcm_response(success=True, message_id="msg_123")

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Urgent Alert",
            body="Immediate notification",
            priority="immediate"
        )

        assert notification is not None
        assert notification.priority == Priority.IMMEDIATE
        assert notification.status == NotificationStatus.SENT

        # Immediate priority should call FCM
        mock_fcm_send.assert_called_once()

    @patch("modules.push_notification.push_notification_service.FCMService.send_multicast")
    def test_send_notification_immediate_multiple_devices(self, mock_fcm_multicast):
        """Test immediate send to multiple devices"""
        self.create_test_device_token(self.account.id, "token_1")
        self.create_test_device_token(self.account.id, "token_2")
        self.create_test_device_token(self.account.id, "token_3")

        mock_fcm_multicast.return_value = self.create_mock_fcm_batch_response(
            success_count=3,
            failure_count=0
        )

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Urgent",
            body="Alert",
            priority="immediate"
        )

        assert notification.status == NotificationStatus.SENT
        mock_fcm_multicast.assert_called_once()

    def test_send_notification_with_data(self):
        """Test sending notification with custom data payload"""
        self.create_test_device_token(self.account.id)

        custom_data = {"type": "message", "id": "123", "sender": "user456"}

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="New Message",
            body="You have a new message",
            data=custom_data,
            priority="normal"
        )

        assert notification.data == custom_data

    def test_send_notification_with_max_retries(self):
        """Test sending notification with custom max_retries"""
        self.create_test_device_token(self.account.id)

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Test",
            body="Test",
            max_retries=5,
            priority="normal"
        )

        assert notification.max_retries == 5

    def test_send_notification_no_devices(self):
        """Test sending notification when account has no devices"""
        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Test",
            body="Test",
            priority="normal"
        )

        assert notification is None

    def test_send_notification_invalid_priority(self):
        """Test sending notification with invalid priority"""
        self.create_test_device_token(self.account.id)

        with self.assertRaises(InvalidPriorityError):
            PushNotificationService.send_notification(
                account_id=self.account.id,
                title="Test",
                body="Test",
                priority="urgent"  # Invalid
            )

    def test_send_notification_sets_expiry(self):
        """Test that notification has correct expiry time"""
        self.create_test_device_token(self.account.id)

        with patch("modules.push_notification.push_notification_service.ConfigService.get_value", return_value=24):
            notification = PushNotificationService.send_notification(
                account_id=self.account.id,
                title="Test",
                body="Test",
                priority="normal"
            )

        assert notification.expires_at is not None
        # Should be approximately 24 hours from now
        expected_expiry = datetime.now() + timedelta(hours=24)
        time_diff = abs((notification.expires_at - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 1 minute

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_notification_immediate_fcm_failure(self, mock_fcm_send):
        """Test immediate send when FCM fails"""
        self.create_test_device_token(self.account.id)
        mock_fcm_send.return_value = self.create_mock_fcm_response(
            success=False,
            error="Network error"
        )

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Test",
            body="Test",
            priority="immediate"
        )

        assert notification.status == NotificationStatus.FAILED

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_notification_immediate_invalid_token(self, mock_fcm_send):
        """Test immediate send with invalid token"""
        self.create_test_device_token(self.account.id)
        mock_fcm_send.side_effect = InvalidTokenError("Invalid token")

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Test",
            body="Test",
            priority="immediate"
        )

        assert notification.status == NotificationStatus.FAILED

    # -------------------------
    # SEND TO USER
    # -------------------------

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_to_user_success(self, mock_fcm_send):
        """Test sending to single user successfully"""
        mock_fcm_send.return_value = self.create_mock_fcm_response(
            success=True,
            message_id="msg_1"
        )

        result = PushNotificationService.send_to_user(
            user_id="user1",
            device_token="token1",
            title="Test",
            body="Hello"
        )

        assert result.success is True
        assert result.message_id == "msg_1"
        assert result.error is None

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_to_user_invalid_token(self, mock_fcm_send):
        """Test sending to user with invalid token"""
        mock_fcm_send.side_effect = InvalidTokenError("bad token")

        result = PushNotificationService.send_to_user(
            user_id="user1",
            device_token="bad_token",
            title="Test",
            body="Hello"
        )

        assert result.success is False
        assert "bad token" in result.error
        assert result.invalid_tokens == ["bad_token"]

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_to_user_with_data(self, mock_fcm_send):
        """Test sending to user with data payload"""
        mock_fcm_send.return_value = self.create_mock_fcm_response(success=True)

        result = PushNotificationService.send_to_user(
            user_id="user1",
            device_token="token1",
            title="Test",
            body="Hello",
            data={"key": "value"}
        )

        assert result.success is True

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_to_user_unexpected_error(self, mock_fcm_send):
        """Test sending to user with unexpected error"""
        mock_fcm_send.side_effect = Exception("Network error")

        result = PushNotificationService.send_to_user(
            user_id="user1",
            device_token="token1",
            title="Test",
            body="Hello"
        )

        assert result.success is False
        assert result.error is not None

    # -------------------------
    # SEND TO MULTIPLE USERS
    # -------------------------

    @patch("modules.push_notification.push_notification_service.FCMService.send_multicast")
    def test_send_to_multiple_users_all_success(self, mock_fcm_multicast):
        """Test sending to multiple users with all success"""
        mock_fcm_multicast.return_value = self.create_mock_fcm_batch_response(
            success_count=3,
            failure_count=0
        )

        result = PushNotificationService.send_to_multiple_users(
            user_tokens={"u1": "t1", "u2": "t2", "u3": "t3"},
            title="Test",
            body="Hello"
        )

        assert result.success is True
        assert len(result.invalid_tokens) == 0

    @patch("modules.push_notification.push_notification_service.FCMService.send_multicast")
    def test_send_to_multiple_users_with_invalid_tokens(self, mock_fcm_multicast):
        """Test sending to multiple users with some invalid tokens"""
        # Create batch response with one invalid token
        good_response = self.create_mock_fcm_response(success=True, message_id="msg1")
        bad_response = self.create_mock_fcm_response(
            success=False,
            error="Invalid token",
            error_code="registration-token-not-registered"
        )

        mock_fcm_multicast.return_value = self.create_mock_fcm_batch_response(
            success_count=1,
            failure_count=1,
            responses=[good_response, bad_response]
        )

        result = PushNotificationService.send_to_multiple_users(
            user_tokens={"u1": "t1", "u2": "bad_token"},
            title="Test",
            body="Hello"
        )

        assert result.success is True  # At least one succeeded
        assert len(result.invalid_tokens) == 1
        assert "bad_token" in result.invalid_tokens

    def test_send_to_multiple_users_empty_tokens(self):
        """Test sending to multiple users with empty token dict"""
        result = PushNotificationService.send_to_multiple_users(
            user_tokens={},
            title="Test",
            body="Hello"
        )

        assert result.success is False
        assert "No device tokens provided" in result.error

    @patch("modules.push_notification.push_notification_service.FCMService.send_multicast")
    def test_send_to_multiple_users_all_fail(self, mock_fcm_multicast):
        """Test sending to multiple users with all failures"""
        mock_fcm_multicast.return_value = self.create_mock_fcm_batch_response(
            success_count=0,
            failure_count=2
        )

        result = PushNotificationService.send_to_multiple_users(
            user_tokens={"u1": "t1", "u2": "t2"},
            title="Test",
            body="Hello"
        )

        assert result.success is False

    # -------------------------
    # SEND TO DEVICES
    # -------------------------

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_send_to_devices_success(self, mock_fcm_send):
        """Test sending to specific device IDs"""
        device1 = self.create_test_device_token(self.account.id, "token_1")
        device2 = self.create_test_device_token(self.account.id, "token_2")

        mock_fcm_send.return_value = self.create_mock_fcm_response(success=True)

        notification = PushNotificationService.send_to_devices(
            device_token_ids=[device1.id, device2.id],
            title="Test",
            body="Hello",
            priority="immediate"
        )

        assert notification is not None
        assert notification.account_id == self.account.id
        assert notification.status == NotificationStatus.SENT
        assert len(notification.device_token_ids) == 2

    def test_send_to_devices_empty_list(self):
        """Test sending to devices with empty list"""
        notification = PushNotificationService.send_to_devices(
            device_token_ids=[],
            title="Test",
            body="Hello"
        )

        assert notification is None

    def test_send_to_devices_no_active_devices(self):
        """Test sending to device IDs that don't exist or aren't active"""
        notification = PushNotificationService.send_to_devices(
            device_token_ids=["507f1f77bcf86cd799439011"],  # Valid ObjectId but doesn't exist
            title="Test",
            body="Hello"
        )

        assert notification is None

    def test_send_to_devices_invalid_priority(self):
        """Test sending to devices with invalid priority"""
        device = self.create_test_device_token(self.account.id)

        with self.assertRaises(InvalidPriorityError):
            PushNotificationService.send_to_devices(
                device_token_ids=[device.id],
                title="Test",
                body="Hello",
                priority="high"  # Invalid
            )

    def test_send_to_devices_normal_priority_queued(self):
        """Test sending to devices with normal priority (queued)"""
        device = self.create_test_device_token(self.account.id)

        notification = PushNotificationService.send_to_devices(
            device_token_ids=[device.id],
            title="Test",
            body="Hello",
            priority="normal"
        )

        assert notification.status == NotificationStatus.PENDING

    # -------------------------
    # GET NOTIFICATION STATUS
    # -------------------------

    @patch("modules.push_notification.push_notification_service.FCMService.send_notification")
    def test_get_notification_status_exists(self, mock_fcm_send):
        """Test getting status of existing notification"""
        self.create_test_device_token(self.account.id)
        mock_fcm_send.return_value = self.create_mock_fcm_response(success=True)

        notification = PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Test",
            body="Test",
            priority="immediate"
        )

        retrieved = PushNotificationService.get_notification_status(
            notification_id=notification.id
        )

        assert retrieved is not None
        assert retrieved.id == notification.id
        assert retrieved.status == NotificationStatus.SENT

    def test_get_notification_status_not_exists(self):
        """Test getting status of non-existent notification"""
        retrieved = PushNotificationService.get_notification_status(
            notification_id="507f1f77bcf86cd799439011"
        )

        assert retrieved is None

    # -------------------------
    # GET PENDING NOTIFICATIONS
    # -------------------------

    def test_get_pending_notifications_empty(self):
        """Test getting pending notifications when none exist"""
        notifications = PushNotificationService.get_pending_notifications()

        assert len(notifications) == 0

    def test_get_pending_notifications_with_pending(self):
        """Test getting pending notifications"""
        device = self.create_test_device_token(self.account.id)

        # Create 3 pending notifications
        for i in range(3):
            PushNotificationService.send_notification(
                account_id=self.account.id,
                title=f"Test {i}",
                body=f"Body {i}",
                priority="normal"
            )

        notifications = PushNotificationService.get_pending_notifications()

        assert len(notifications) == 3
        assert all(n.status == NotificationStatus.PENDING for n in notifications)

    def test_get_pending_notifications_with_limit(self):
        """Test getting pending notifications with limit"""
        device = self.create_test_device_token(self.account.id)

        # Create 5 pending notifications
        for i in range(5):
            PushNotificationService.send_notification(
                account_id=self.account.id,
                title=f"Test {i}",
                body=f"Body {i}",
                priority="normal"
            )

        notifications = PushNotificationService.get_pending_notifications(limit=2)

        assert len(notifications) == 2

    def test_get_pending_notifications_with_skip(self):
        """Test getting pending notifications with skip"""
        device = self.create_test_device_token(self.account.id)

        # Create 5 pending notifications
        for i in range(5):
            PushNotificationService.send_notification(
                account_id=self.account.id,
                title=f"Test {i}",
                body=f"Body {i}",
                priority="normal"
            )

        all_notifications = PushNotificationService.get_pending_notifications()
        skipped_notifications = PushNotificationService.get_pending_notifications(skip=2)

        assert len(skipped_notifications) == 3

    # -------------------------
    # GET ACCOUNT NOTIFICATIONS
    # -------------------------

    def test_get_account_notifications_empty(self):
        """Test getting account notifications when none exist"""
        notifications = PushNotificationService.get_account_notifications(
            account_id=self.account.id
        )

        assert len(notifications) == 0

    def test_get_account_notifications_with_data(self):
        """Test getting account notifications"""
        device = self.create_test_device_token(self.account.id)

        # Create notifications for account
        for i in range(3):
            PushNotificationService.send_notification(
                account_id=self.account.id,
                title=f"Test {i}",
                body=f"Body {i}",
                priority="normal"
            )

        notifications = PushNotificationService.get_account_notifications(
            account_id=self.account.id
        )

        assert len(notifications) == 3
        assert all(n.account_id == self.account.id for n in notifications)

    def test_get_account_notifications_different_accounts(self):
        """Test that notifications are scoped to correct account"""
        account2 = self.create_test_account("other@example.com")

        device1 = self.create_test_device_token(self.account.id, "token_1")
        device2 = self.create_test_device_token(account2.id, "token_2")

        PushNotificationService.send_notification(
            account_id=self.account.id,
            title="Account 1",
            body="Test",
            priority="normal"
        )
        PushNotificationService.send_notification(
            account_id=account2.id,
            title="Account 2",
            body="Test",
            priority="normal"
        )

        account1_notifications = PushNotificationService.get_account_notifications(
            account_id=self.account.id
        )
        account2_notifications = PushNotificationService.get_account_notifications(
            account_id=account2.id
        )

        assert len(account1_notifications) == 1
        assert len(account2_notifications) == 1
        assert account1_notifications[0].title == "Account 1"
        assert account2_notifications[0].title == "Account 2"

    def test_get_account_notifications_with_limit(self):
        """Test getting account notifications with limit"""
        device = self.create_test_device_token(self.account.id)

        for i in range(5):
            PushNotificationService.send_notification(
                account_id=self.account.id,
                title=f"Test {i}",
                body="Test",
                priority="normal"
            )

        notifications = PushNotificationService.get_account_notifications(
            account_id=self.account.id,
            limit=3
        )

        assert len(notifications) == 3
