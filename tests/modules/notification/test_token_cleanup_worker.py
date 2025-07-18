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
        # Mock the configuration value
        mock_get_value.return_value = 45  # Mock 45 days for cleanup

        # Set up the mock cleanup to return a count
        mock_cleanup.return_value = 5

        # Run the worker's execute method
        await TokenCleanupWorker.execute()

        # Verify the service was called with the correct parameter
        mock_get_value.assert_called_with(key="notification.token_cleanup_days", default=60)
        mock_cleanup.assert_called_with(days=45)

    @patch.object(NotificationService, "cleanup_inactive_tokens")
    async def test_execute_handles_exceptions(self, mock_cleanup) -> None:
        # Set up the mock to raise an exception
        mock_cleanup.side_effect = Exception("Test error")

        # Verify the execute method raises the exception (doesn't swallow it)
        with self.assertRaises(Exception):
            await TokenCleanupWorker.execute()

    @patch.object(NotificationService, "cleanup_inactive_tokens")
    @patch.object(ConfigService, "get_value")
    async def test_run_invokes_execute(self, mock_get_value, mock_cleanup) -> None:
        # Set up mocks
        mock_get_value.return_value = 30
        mock_cleanup.return_value = 3

        # Create an instance of the worker
        worker = TokenCleanupWorker()

        # Use patch to capture calls to super().run()
        with patch.object(BaseWorker, "run") as mock_super_run:
            # Run the worker
            await worker.run()

            # Verify that super().run() was called (which is what triggers execute())
            mock_super_run.assert_called_once()

    @patch("modules.application.application_service.WorkerManager")
    def test_schedule_worker_as_cron(self, mock_worker_manager) -> None:
        # Set up the mock
        mock_worker_manager.schedule_worker_as_cron.return_value = "worker-id-123"

        # Schedule the worker
        worker_id = ApplicationService.schedule_worker_as_cron(cls=TokenCleanupWorker, cron_schedule="0 2 * * 0")

        # Verify the worker was scheduled with the correct parameters
        mock_worker_manager.schedule_worker_as_cron.assert_called_with(
            cls=TokenCleanupWorker, cron_schedule="0 2 * * 0"
        )
        self.assertEqual(worker_id, "worker-id-123")

    def test_integration_execute_method(self) -> None:
        # Create tokens with various activity dates
        now = datetime.now()

        # Register recent tokens
        NotificationService.register_device_token(
            params=RegisterDeviceTokenParams(
                user_id="user1", token="active-token-1", device_type="android", app_version="1.0"
            )
        )

        # Register older tokens by manipulating the last_active date
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

        # Get initial count of tokens
        initial_count = DeviceTokenRepository.collection().count_documents({})
        self.assertEqual(initial_count, 3)

        # Run the worker execute method directly
        asyncio.run(TokenCleanupWorker.execute())

        # Verify inactive tokens were removed
        remaining_tokens = list(DeviceTokenRepository.collection().find())
        self.assertEqual(len(remaining_tokens), 1)
        self.assertEqual(remaining_tokens[0]["token"], "active-token-1")


