from datetime import datetime, timedelta
from unittest.mock import patch

from modules.notification.internals.device_token_reader import DeviceTokenReader
from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.device_token_writer import DeviceTokenWriter
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams
from tests.modules.notification.base_test_notification import BaseTestNotification


class TestDeviceTokenService(BaseTestNotification):
    def test_register_new_device_token(self) -> None:
        params = RegisterDeviceTokenParams(
            user_id="user123", token="fcm-token-123456", device_type="android", app_version="1.0.0"
        )
        device_token = NotificationService.register_device_token(params=params)
        self.assertEqual(device_token.token, "fcm-token-123456")
        self.assertEqual(device_token.device_type, "android")
        self.assertEqual(device_token.app_version, "1.0.0")
        stored_token = DeviceTokenReader.get_token_by_value("fcm-token-123456")
        self.assertIsNotNone(stored_token)
        self.assertEqual(stored_token.user_id, "user123")
        self.assertEqual(stored_token.token, "fcm-token-123456")
        self.assertEqual(stored_token.device_type, "android")
        self.assertEqual(stored_token.app_version, "1.0.0")

    def test_update_existing_device_token(self) -> None:
        params1 = RegisterDeviceTokenParams(
            user_id="user123", token="fcm-token-123456", device_type="android", app_version="1.0.0"
        )
        NotificationService.register_device_token(params=params1)
        params2 = RegisterDeviceTokenParams(
            user_id="user456", token="fcm-token-123456", device_type="android", app_version="2.0.0"
        )
        updated_token = NotificationService.register_device_token(params=params2)
        self.assertEqual(updated_token.token, "fcm-token-123456")
        self.assertEqual(updated_token.device_type, "android")
        self.assertEqual(updated_token.app_version, "2.0.0")
        stored_token = DeviceTokenReader.get_token_by_value("fcm-token-123456")
        self.assertIsNotNone(stored_token)
        self.assertEqual(stored_token.user_id, "user456")
        self.assertEqual(stored_token.app_version, "2.0.0")

    def test_remove_device_token(self) -> None:
        params = RegisterDeviceTokenParams(
            user_id="user123", token="fcm-token-123456", device_type="android", app_version="1.0.0"
        )
        NotificationService.register_device_token(params=params)
        self.assertIsNotNone(DeviceTokenReader.get_token_by_value("fcm-token-123456"))
        result = NotificationService.remove_device_token(token="fcm-token-123456")
        self.assertTrue(result)
        self.assertIsNone(DeviceTokenReader.get_token_by_value("fcm-token-123456"))

    def test_remove_nonexistent_device_token(self) -> None:
        result = NotificationService.remove_device_token(token="nonexistent-token")
        self.assertFalse(result)

    def test_get_device_tokens_by_user_id(self) -> None:
        params1 = RegisterDeviceTokenParams(
            user_id="user123", token="fcm-token-1", device_type="android", app_version="1.0.0"
        )
        params2 = RegisterDeviceTokenParams(
            user_id="user123", token="fcm-token-2", device_type="ios", app_version="1.0.0"
        )
        params3 = RegisterDeviceTokenParams(
            user_id="user456", token="fcm-token-3", device_type="web", app_version="1.0.0"
        )
        NotificationService.register_device_token(params=params1)
        NotificationService.register_device_token(params=params2)
        NotificationService.register_device_token(params=params3)
        tokens = NotificationService.get_device_tokens_by_user_id(user_id="user123")
        self.assertEqual(len(tokens), 2)
        self.assertIn("fcm-token-1", tokens)
        self.assertIn("fcm-token-2", tokens)
        self.assertNotIn("fcm-token-3", tokens)
        tokens = NotificationService.get_device_tokens_by_user_id(user_id="user456")
        self.assertEqual(len(tokens), 1)
        self.assertIn("fcm-token-3", tokens)

    def test_update_token_activity(self) -> None:
        params = RegisterDeviceTokenParams(
            user_id="user123", token="fcm-token-123456", device_type="android", app_version="1.0.0"
        )
        NotificationService.register_device_token(params=params)
        with patch.object(DeviceTokenUtil, "get_current_timestamp") as mock_timestamp:
            new_time = datetime.now() + timedelta(days=1)
            mock_timestamp.return_value = new_time
            NotificationService.update_token_activity(token="fcm-token-123456")
            token = DeviceTokenReader.get_token_by_value("fcm-token-123456")
            self.assertIsNotNone(token)
            self.assertEqual(token.last_active.replace(microsecond=0), new_time.replace(microsecond=0))

    @patch.object(DeviceTokenUtil, "calculate_cutoff_date")
    def test_cleanup_inactive_tokens(self, mock_cutoff_date) -> None:
        cutoff_time = datetime.now() - timedelta(days=30)
        mock_cutoff_date.return_value = cutoff_time
        active_token = DeviceTokenWriter.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user1", token="active-token", device_type="android", app_version="1.0"
            )
        )
        inactive_token_model = DeviceTokenWriter.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user2", token="inactive-token", device_type="ios", app_version="1.0"
            )
        )
        DeviceTokenRepository.collection().update_one(
            {"token": "inactive-token"}, {"$set": {"last_active": datetime.now() - timedelta(days=60)}}
        )
        deleted_count = NotificationService.cleanup_inactive_tokens(days=30)
        self.assertEqual(deleted_count, 1)
        self.assertIsNotNone(DeviceTokenReader.get_token_by_value("active-token"))
        self.assertIsNone(DeviceTokenReader.get_token_by_value("inactive-token"))

    @patch.object(DeviceTokenUtil, "calculate_activity_cutoff_date")
    def test_get_active_tokens(self, mock_cutoff_date) -> None:
        cutoff_time = datetime.now() - timedelta(days=15)
        mock_cutoff_date.return_value = cutoff_time
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user1", token="active-token-1", device_type="android", app_version="1.0"
            )
        )
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user2", token="active-token-2", device_type="ios", app_version="1.0"
            )
        )
        inactive_token = NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user3", token="inactive-token", device_type="web", app_version="1.0"
            )
        )
        DeviceTokenRepository.collection().update_one(
            {"token": "inactive-token"}, {"$set": {"last_active": datetime.now() - timedelta(days=30)}}
        )
        active_tokens = NotificationService.get_active_tokens(days=15)
        self.assertEqual(len(active_tokens), 2)
        self.assertIn("active-token-1", active_tokens)
        self.assertIn("active-token-2", active_tokens)
        self.assertNotIn("inactive-token", active_tokens)
