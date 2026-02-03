from unittest.mock import MagicMock, patch

import requests

from modules.application.workers.health_check_worker import HealthCheckWorker

TEST_HEALTH_CHECK_URL = "http://localhost:8080/api/"


class TestGivenBackendIsRunning:
    class TestWhenHealthCheckReturns200:
        @patch("modules.application.workers.health_check_worker.ConfigService")
        @patch("modules.application.workers.health_check_worker.requests.get")
        @patch("modules.application.workers.health_check_worker.Logger.info")
        def test_then_logs_healthy_status(
            self,
            mock_logger_info: MagicMock,
            mock_requests_get: MagicMock,
            mock_config_service: MagicMock,
        ) -> None:
            mock_config_service.__getitem__.return_value.get_value.return_value = (
                TEST_HEALTH_CHECK_URL
            )
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_requests_get.return_value = mock_response

            HealthCheckWorker.perform()

            mock_requests_get.assert_called_once_with(TEST_HEALTH_CHECK_URL, timeout=3)
            mock_logger_info.assert_called_once_with(message="Backend is healthy")

    class TestWhenHealthCheckReturns500:
        @patch("modules.application.workers.health_check_worker.ConfigService")
        @patch("modules.application.workers.health_check_worker.requests.get")
        @patch("modules.application.workers.health_check_worker.Logger.error")
        def test_then_logs_unhealthy_status_with_code(
            self,
            mock_logger_error: MagicMock,
            mock_requests_get: MagicMock,
            mock_config_service: MagicMock,
        ) -> None:
            mock_config_service.__getitem__.return_value.get_value.return_value = (
                TEST_HEALTH_CHECK_URL
            )
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_requests_get.return_value = mock_response

            HealthCheckWorker.perform()

            mock_requests_get.assert_called_once_with(TEST_HEALTH_CHECK_URL, timeout=3)
            mock_logger_error.assert_called_once_with(message="Backend is unhealthy: status 500")

    class TestWhenHealthCheckReturns404:
        @patch("modules.application.workers.health_check_worker.ConfigService")
        @patch("modules.application.workers.health_check_worker.requests.get")
        @patch("modules.application.workers.health_check_worker.Logger.error")
        def test_then_logs_unhealthy_status_with_code(
            self,
            mock_logger_error: MagicMock,
            mock_requests_get: MagicMock,
            mock_config_service: MagicMock,
        ) -> None:
            mock_config_service.__getitem__.return_value.get_value.return_value = (
                TEST_HEALTH_CHECK_URL
            )
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_requests_get.return_value = mock_response

            HealthCheckWorker.perform()

            mock_requests_get.assert_called_once_with(TEST_HEALTH_CHECK_URL, timeout=3)
            mock_logger_error.assert_called_once_with(message="Backend is unhealthy: status 404")


class TestGivenBackendIsUnreachable:
    class TestWhenRequestTimesOut:
        @patch("modules.application.workers.health_check_worker.ConfigService")
        @patch("modules.application.workers.health_check_worker.requests.get")
        @patch("modules.application.workers.health_check_worker.Logger.error")
        def test_then_logs_timeout_error(
            self,
            mock_logger_error: MagicMock,
            mock_requests_get: MagicMock,
            mock_config_service: MagicMock,
        ) -> None:
            mock_config_service.__getitem__.return_value.get_value.return_value = (
                TEST_HEALTH_CHECK_URL
            )
            mock_requests_get.side_effect = requests.Timeout("Connection timed out")

            HealthCheckWorker.perform()

            mock_requests_get.assert_called_once_with(TEST_HEALTH_CHECK_URL, timeout=3)
            mock_logger_error.assert_called_once()
            error_message = mock_logger_error.call_args[1]["message"]
            assert "Backend is unhealthy:" in error_message
            assert "timed out" in error_message.lower()

    class TestWhenConnectionFails:
        @patch("modules.application.workers.health_check_worker.ConfigService")
        @patch("modules.application.workers.health_check_worker.requests.get")
        @patch("modules.application.workers.health_check_worker.Logger.error")
        def test_then_logs_connection_error(
            self,
            mock_logger_error: MagicMock,
            mock_requests_get: MagicMock,
            mock_config_service: MagicMock,
        ) -> None:
            mock_config_service.__getitem__.return_value.get_value.return_value = (
                TEST_HEALTH_CHECK_URL
            )
            mock_requests_get.side_effect = requests.ConnectionError("Connection refused")

            HealthCheckWorker.perform()

            mock_requests_get.assert_called_once_with(TEST_HEALTH_CHECK_URL, timeout=3)
            mock_logger_error.assert_called_once()
            error_message = mock_logger_error.call_args[1]["message"]
            assert "Backend is unhealthy:" in error_message
            assert "refused" in error_message.lower()

    class TestWhenUnexpectedExceptionOccurs:
        @patch("modules.application.workers.health_check_worker.ConfigService")
        @patch("modules.application.workers.health_check_worker.requests.get")
        @patch("modules.application.workers.health_check_worker.Logger.error")
        def test_then_logs_generic_error(
            self,
            mock_logger_error: MagicMock,
            mock_requests_get: MagicMock,
            mock_config_service: MagicMock,
        ) -> None:
            mock_config_service.__getitem__.return_value.get_value.return_value = (
                TEST_HEALTH_CHECK_URL
            )
            mock_requests_get.side_effect = Exception("Unexpected error")

            HealthCheckWorker.perform()

            mock_requests_get.assert_called_once_with(TEST_HEALTH_CHECK_URL, timeout=3)
            mock_logger_error.assert_called_once()
            error_message = mock_logger_error.call_args[1]["message"]
            assert "Backend is unhealthy:" in error_message
            assert "Unexpected error" in error_message


class TestGivenWorkerConfiguration:
    class TestWhenInspectingWorkerSettings:
        def test_then_has_correct_queue(self) -> None:
            assert HealthCheckWorker.queue == "default"

        def test_then_has_correct_max_retries(self) -> None:
            assert HealthCheckWorker.max_retries == 1

        def test_then_has_correct_cron_schedule(self) -> None:
            assert HealthCheckWorker.cron_schedule == "*/10 * * * *"
