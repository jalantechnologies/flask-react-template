from datetime import datetime, timedelta
from unittest.mock import patch

from modules.notification.notification_service import NotificationService
from modules.notification.types import DeviceTokenInfo, RegisterDeviceTokenParams
from server import app

from tests.modules.notification.base_test_notification import BaseTestNotification


class TestDeviceTokenService(BaseTestNotification):
    def test_register_device_token(self) -> None:
        token_params = RegisterDeviceTokenParams(
            user_id="user123",
            token="fcm-token-123",
            device_type="android",
            app_version="1.0.0",
        )
        device_token = NotificationService.register_device_token(params=token_params)
        self.assertIsInstance(device_token, DeviceTokenInfo)
        self.assertEqual(device_token.token, token_params.token)
        self.assertEqual(device_token.device_type, token_params.device_type)
        self.assertEqual(device_token.app_version, token_params.app_version)
        tokens = NotificationService.get_device_tokens_by_user_id(token_params.user_id)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], token_params.token)

    def test_update_existing_device_token(self) -> None:
        initial_params = RegisterDeviceTokenParams(
            user_id="user123",
            token="fcm-token-123",
            device_type="android",
            app_version="1.0.0",
        )
        NotificationService.register_device_token(params=initial_params)
        updated_params = RegisterDeviceTokenParams(
            user_id="user456",
            token="fcm-token-123",
            device_type="ios",
            app_version="2.0.0",
        )
        updated_token = NotificationService.register_device_token(params=updated_params)
        self.assertEqual(updated_token.token, updated_params.token)
        self.assertEqual(updated_token.device_type, updated_params.device_type)
        self.assertEqual(updated_token.app_version, updated_params.app_version)
        tokens = NotificationService.get_device_tokens_by_user_id(
            updated_params.user_id
        )
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], updated_params.token)
        original_user_tokens = NotificationService.get_device_tokens_by_user_id(
            initial_params.user_id
        )
        self.assertEqual(len(original_user_tokens), 0)

    def test_remove_device_token(self) -> None:
        token_params = RegisterDeviceTokenParams(
            user_id="user123",
            token="fcm-token-123",
            device_type="android",
            app_version="1.0.0",
        )
        NotificationService.register_device_token(params=token_params)
        result = NotificationService.remove_device_token(token_params.token)
        self.assertTrue(result)
        tokens = NotificationService.get_device_tokens_by_user_id(token_params.user_id)
        self.assertEqual(len(tokens), 0)

    def test_remove_nonexistent_device_token(self) -> None:
        result = NotificationService.remove_device_token("nonexistent-token")
        self.assertFalse(result)

    def test_get_tokens_by_user_id_empty(self) -> None:
        tokens = NotificationService.get_device_tokens_by_user_id("nonexistent-user")
        self.assertEqual(len(tokens), 0)

    def test_get_tokens_by_user_id_multiple(self) -> None:
        user_id = "user123"
        tokens = ["token1", "token2", "token3"]
        for i, token in enumerate(tokens):
            params = RegisterDeviceTokenParams(
                user_id=user_id,
                token=token,
                device_type=f"device{i}",
                app_version="1.0.0",
            )
            NotificationService.register_device_token(params=params)
        result_tokens = NotificationService.get_device_tokens_by_user_id(user_id)
        self.assertEqual(len(result_tokens), len(tokens))
        for token in tokens:
            self.assertIn(token, result_tokens)

    @patch(
        "modules.notification.internals.device_token_util.DeviceTokenUtil.calculate_cutoff_date"
    )
    def test_cleanup_inactive_tokens(self, mock_calculate_cutoff_date) -> None:
        cutoff_date = datetime.now() - timedelta(days=30)
        mock_calculate_cutoff_date.return_value = cutoff_date
        active_params = RegisterDeviceTokenParams(
            user_id="user1",
            token="active-token",
            device_type="android",
            app_version="1.0.0",
        )
        NotificationService.register_device_token(params=active_params)
        inactive_params = RegisterDeviceTokenParams(
            user_id="user2",
            token="inactive-token",
            device_type="ios",
            app_version="1.0.0",
        )
        NotificationService.register_device_token(params=inactive_params)
        DeviceTokenRepository.collection().update_one(
            {"token": inactive_params.token},
            {"$set": {"last_active": cutoff_date - timedelta(days=1)}},
        )
        deleted_count = NotificationService.cleanup_inactive_tokens(days=30)
        self.assertEqual(deleted_count, 1)
        active_tokens = NotificationService.get_device_tokens_by_user_id("user1")
        self.assertEqual(len(active_tokens), 1)
        inactive_tokens = NotificationService.get_device_tokens_by_user_id("user2")
        self.assertEqual(len(inactive_tokens), 0)

    @patch(
        "modules.notification.internals.device_token_util.DeviceTokenUtil.calculate_activity_cutoff_date"
    )
    def test_get_active_tokens(self, mock_calculate_activity_cutoff_date) -> None:
        cutoff_date = datetime.now() - timedelta(days=30)
        mock_calculate_activity_cutoff_date.return_value = cutoff_date
        active_params = RegisterDeviceTokenParams(
            user_id="user1",
            token="active-token",
            device_type="android",
            app_version="1.0.0",
        )
        NotificationService.register_device_token(params=active_params)
        inactive_params = RegisterDeviceTokenParams(
            user_id="user2",
            token="inactive-token",
            device_type="ios",
            app_version="1.0.0",
        )
        NotificationService.register_device_token(params=inactive_params)
        DeviceTokenRepository.collection().update_one(
            {"token": inactive_params.token},
            {"$set": {"last_active": cutoff_date - timedelta(days=1)}},
        )
        active_tokens = NotificationService.get_active_tokens(days=30)
        self.assertEqual(len(active_tokens), 1)
        self.assertIn("active-token", active_tokens)
        self.assertNotIn("inactive-token", active_tokens)
