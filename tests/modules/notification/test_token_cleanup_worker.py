import asyncio
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from modules.application.application_service import ApplicationService
from modules.application.types import BaseWorker
from modules.config.config_service import ConfigService
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams
from modules.notification.workers.token_cleanup_worker import TokenCleanupWorker
from tests.modules.notification.base_test_notification import BaseTestNotification


class TestTokenCleanupWorker(BaseTestNotification):
    @patch.object(NotificationService, "cleanup_inactive_tokens")
    @patch.object(ConfigService, "get_value")
    async def test_execute_calls_cleanup_service(self, mock_get_value, mock_cleanup) -> None:
        mock_get_value.return_value = 45
        mock_cleanup.return_value = 5
        await TokenCleanupWorker.execute()
        mock_get_value.assert_called_with(key="notification.token_cleanup_days", default=60)
        mock_cleanup.assert_called_with(days=45)

    @patch.object(NotificationService, "cleanup_inactive_tokens")
    async def test_execute_handles_exceptions(self, mock_cleanup) -> None:
        mock_cleanup.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await TokenCleanupWorker.execute()

    @patch.object(NotificationService, "cleanup_inactive_tokens")
    @patch.object(ConfigService, "get_value")
    async def test_run_invokes_execute(self, mock_get_value, mock_cleanup) -> None:
        mock_get_value.return_value = 30
        mock_cleanup.return_value = 3
        worker = TokenCleanupWorker()
        with patch.object(BaseWorker, "run") as mock_super_run:
            await worker.run()
            mock_super_run.assert_called_once()

    @patch("modules.application.application_service.WorkerManager")
    def test_schedule_worker_as_cron(self, mock_worker_manager) -> None:
        mock_worker_manager.schedule_worker_as_cron.return_value = "worker-id-123"
        worker_id = ApplicationService.schedule_worker_as_cron(cls=TokenCleanupWorker, cron_schedule="0 2 * * 0")
        mock_worker_manager.schedule_worker_as_cron.assert_called_with(
            cls=TokenCleanupWorker, cron_schedule="0 2 * * 0"
        )
        self.assertEqual(worker_id, "worker-id-123")

    def test_integration_execute_method(self) -> None:
        now = datetime.now()
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user1", token="active-token-1", device_type="android", app_version="1.0"
            )
        )
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user2", token="inactive-token-1", device_type="ios", app_version="1.0"
            )
        )
        DeviceTokenRepository.collection().update_one(
            {"token": "inactive-token-1"}, {"$set": {"last_active": now - timedelta(days=90)}}
        )
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user3", token="inactive-token-2", device_type="web", app_version="1.0"
            )
        )
        DeviceTokenRepository.collection().update_one(
            {"token": "inactive-token-2"}, {"$set": {"last_active": now - timedelta(days=100)}}
        )
        initial_count = DeviceTokenRepository.collection().count_documents({})
        self.assertEqual(initial_count, 3)
        asyncio.run(TokenCleanupWorker.execute())
        remaining_tokens = list(DeviceTokenRepository.collection().find())
        self.assertEqual(len(remaining_tokens), 1)
        self.assertEqual(remaining_tokens[0]["token"], "active-token-1")
