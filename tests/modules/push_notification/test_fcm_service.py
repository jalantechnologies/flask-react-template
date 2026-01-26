# tests/modules/push_notification/test_fcm_service.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

from modules.push_notification.fcm_service import FCMService
from modules.push_notification.errors import (
    InvalidTokenError,
    FCMQuotaExceededError,
    FCMAuthError,
    FCMError,
)
from tests.modules.push_notification.base_test_push_notification import BaseTestPushNotification


class TestFCMService(BaseTestPushNotification):
    """Comprehensive tests for FCM Service"""

    def setup_method(self, method=None):
        self._ensure_messaging_exceptions()

    @staticmethod
    def _ensure_messaging_exceptions():
        """Ensure messaging module has expected exception types for tests."""
        if not hasattr(messaging, "QuotaExceededError"):
            messaging.QuotaExceededError = type("QuotaExceededError", (Exception,), {})
        if not hasattr(messaging, "ThirdPartyAuthError"):
            messaging.ThirdPartyAuthError = type("ThirdPartyAuthError", (Exception,), {})
        if not hasattr(messaging, "UnregisteredError"):
            messaging.UnregisteredError = type("UnregisteredError", (Exception,), {})

    # -------------------------
    # INITIALIZATION
    # -------------------------

    @patch("modules.push_notification.fcm_service.firebase_admin.initialize_app")
    @patch("modules.push_notification.fcm_service.credentials.Certificate")
    @patch.object(Path, "exists", return_value=True)
    def test_initialize_success(self, mock_exists, mock_cert, mock_init_app):
        """Test successful FCM initialization"""
        self._ensure_messaging_exceptions()
        FCMService._initialized = False
        mock_app = MagicMock()
        mock_init_app.return_value = mock_app

        with patch("modules.push_notification.fcm_service.ConfigService.get_value") as mock_config:
            mock_config.side_effect = lambda key: {
                "firebase.project_id": "test-project",
                "firebase.credentials_path": "/path/to/creds.json"
            }[key]

            FCMService.initialize()

            assert FCMService._initialized is True
            assert FCMService._app == mock_app
            mock_init_app.assert_called_once()

    def test_initialize_already_initialized(self):
        """Test initializing when already initialized"""
        FCMService._initialized = True
        FCMService._app = MagicMock()

        FCMService.initialize()

        assert FCMService._initialized is True

    @patch("modules.push_notification.fcm_service.ConfigService.get_value")
    def test_initialize_missing_project_id(self, mock_config):
        """Test initialization fails with missing project_id"""
        FCMService._initialized = False
        mock_config.side_effect = lambda key: None if key == "firebase.project_id" else "/path"

        with pytest.raises(FCMError) as exc_info:
            FCMService.initialize()

        assert "Missing firebase.project_id" in str(exc_info.value)

    @patch("modules.push_notification.fcm_service.ConfigService.get_value")
    def test_initialize_missing_credentials_path(self, mock_config):
        """Test initialization fails with missing credentials_path"""
        FCMService._initialized = False
        mock_config.side_effect = lambda key: None if key == "firebase.credentials_path" else "test-project"

        with pytest.raises(FCMError) as exc_info:
            FCMService.initialize()

        assert "Missing firebase.credentials_path" in str(exc_info.value)

    @patch("modules.push_notification.fcm_service.firebase_admin.initialize_app")
    @patch("modules.push_notification.fcm_service.credentials.Certificate")
    @patch.object(Path, "exists", return_value=False)
    def test_initialize_credentials_not_found(self, mock_exists, mock_cert, mock_init_app):
        """Test initialization fails when credentials file not found"""
        FCMService._initialized = False

        with patch("modules.push_notification.fcm_service.ConfigService.get_value") as mock_config:
            mock_config.side_effect = lambda key: {
                "firebase.project_id": "test-project",
                "firebase.credentials_path": "/nonexistent/path.json"
            }[key]

            with pytest.raises(FCMError) as exc_info:
                FCMService.initialize()

            assert "credentials not found" in str(exc_info.value).lower()

    def test_ensure_initialized_raises_when_not_initialized(self):
        """Test _ensure_initialized raises error when not initialized"""
        FCMService._initialized = False

        with pytest.raises(FCMError) as exc_info:
            FCMService._ensure_initialized()

        assert "not initialized" in str(exc_info.value).lower()

    # -------------------------
    # SEND NOTIFICATION
    # -------------------------

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_success(self, mock_send):
        """Test successful notification send"""
        mock_send.return_value = "msg_123"

        result = FCMService.send_notification(
            device_token="token123",
            title="Test",
            body="Hello"
        )

        assert result.success is True
        assert result.message_id == "msg_123"
        assert result.error is None
        mock_send.assert_called_once()

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_with_data(self, mock_send):
        """Test notification send with data payload"""
        mock_send.return_value = "msg_124"

        result = FCMService.send_notification(
            device_token="token123",
            title="Test",
            body="Hello",
            data={"key": "value", "id": "123"}
        )

        assert result.success is True
        assert result.message_id == "msg_124"

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_immediate_priority(self, mock_send):
        """Test notification with immediate priority"""
        mock_send.return_value = "msg_125"

        result = FCMService.send_notification(
            device_token="token123",
            title="Urgent",
            body="Critical alert",
            priority="immediate"
        )

        assert result.success is True
        
        # Verify the message was constructed with correct priority settings
        call_args = mock_send.call_args[0][0]
        assert call_args.android.priority == "immediate"
        assert call_args.apns.headers["apns-priority"] == "10"

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_normal_priority(self, mock_send):
        """Test notification with normal priority"""
        mock_send.return_value = "msg_126"

        result = FCMService.send_notification(
            device_token="token123",
            title="Test",
            body="Normal message",
            priority="normal"
        )

        assert result.success is True
        
        # Verify normal priority settings
        call_args = mock_send.call_args[0][0]
        assert call_args.android.priority == "normal"
        assert call_args.apns.headers["apns-priority"] == "5"

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_invalid_token(self, mock_send):
        """Test notification with invalid/unregistered token"""
        mock_send.side_effect = messaging.UnregisteredError("bad token")

        with pytest.raises(InvalidTokenError) as exc_info:
            FCMService.send_notification(
                device_token="bad_token",
                title="Test",
                body="Hello"
            )

        assert "invalid or unregistered" in str(exc_info.value).lower()

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_quota_exceeded(self, mock_send):
        """Test notification when FCM quota exceeded"""
        mock_send.side_effect = messaging.QuotaExceededError("quota")

        with pytest.raises(FCMQuotaExceededError) as exc_info:
            FCMService.send_notification(
                device_token="token",
                title="Test",
                body="Hello"
            )

        assert "quota exceeded" in str(exc_info.value).lower()

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_auth_error(self, mock_send):
        """Test notification with authentication error"""
        mock_send.side_effect = messaging.ThirdPartyAuthError("auth")

        with pytest.raises(FCMAuthError) as exc_info:
            FCMService.send_notification(
                device_token="token",
                title="Test",
                body="Hello"
            )

        assert "authentication failed" in str(exc_info.value).lower()

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_firebase_error(self, mock_send):
        """Test notification with generic Firebase error"""
        firebase_error = FirebaseError("UNKNOWN", "Unknown error")
        mock_send.side_effect = firebase_error

        result = FCMService.send_notification(
            device_token="token",
            title="Test",
            body="Hello"
        )

        assert result.success is False
        assert result.error is not None
        assert "Unknown error" in result.error

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_send_notification_unexpected_error(self, mock_send):
        """Test notification with unexpected error"""
        mock_send.side_effect = Exception("Unexpected error")

        with pytest.raises(FCMError) as exc_info:
            FCMService.send_notification(
                device_token="token",
                title="Test",
                body="Hello"
            )

        assert "Failed to send notification" in str(exc_info.value)

    # -------------------------
    # MULTICAST
    # -------------------------

    @patch("modules.push_notification.fcm_service.messaging.send_multicast", create=True)
    def test_send_multicast_success_all(self, mock_send_multicast):
        """Test multicast with all successful sends"""
        response = MagicMock()
        response.success_count = 3
        response.failure_count = 0

        success_resp = MagicMock(success=True, message_id="msg_1", exception=None)
        response.responses = [success_resp, success_resp, success_resp]

        mock_send_multicast.return_value = response

        result = FCMService.send_multicast(
            device_tokens=["t1", "t2", "t3"],
            title="Test",
            body="Hello"
        )

        assert result.success_count == 3
        assert result.failure_count == 0
        assert len(result.responses) == 3
        assert all(r.success for r in result.responses)

    @patch("modules.push_notification.fcm_service.messaging.send_multicast", create=True)
    def test_send_multicast_partial_success(self, mock_send_multicast):
        """Test multicast with partial success"""
        response = MagicMock()
        response.success_count = 2
        response.failure_count = 1

        success_resp = MagicMock(success=True, message_id="msg_1", exception=None)
        failure_resp = MagicMock(
            success=False,
            exception=messaging.UnregisteredError("invalid"),
            message_id=None
        )
        response.responses = [success_resp, success_resp, failure_resp]

        mock_send_multicast.return_value = response

        result = FCMService.send_multicast(
            device_tokens=["t1", "t2", "t3"],
            title="Test",
            body="Hello"
        )

        assert result.success_count == 2
        assert result.failure_count == 1
        assert len(result.responses) == 3
        assert sum(1 for r in result.responses if r.success) == 2
        assert sum(1 for r in result.responses if not r.success) == 1

    @patch("modules.push_notification.fcm_service.messaging.send_multicast", create=True)
    def test_send_multicast_with_data_and_priority(self, mock_send_multicast):
        """Test multicast with data payload and priority"""
        response = MagicMock()
        response.success_count = 2
        response.failure_count = 0

        success_resp = MagicMock(success=True, message_id="msg_1", exception=None)
        response.responses = [success_resp, success_resp]

        mock_send_multicast.return_value = response

        result = FCMService.send_multicast(
            device_tokens=["t1", "t2"],
            title="Test",
            body="Hello",
            data={"key": "value"},
            priority="immediate"
        )

        assert result.success_count == 2
        mock_send_multicast.assert_called_once()

    def test_send_multicast_empty_tokens(self):
        """Test multicast with empty token list"""
        result = FCMService.send_multicast(
            device_tokens=[],
            title="Test",
            body="Hello"
        )

        assert result.success_count == 0
        assert result.failure_count == 0
        assert len(result.responses) == 0

    def test_send_multicast_too_many_tokens(self):
        """Test multicast with more than 500 tokens"""
        tokens = [f"token_{i}" for i in range(501)]

        with pytest.raises(FCMError) as exc_info:
            FCMService.send_multicast(
                device_tokens=tokens,
                title="Test",
                body="Hello"
            )

        assert "maximum 500 tokens" in str(exc_info.value).lower()

    @patch("modules.push_notification.fcm_service.messaging.send_multicast", create=True)
    def test_send_multicast_quota_exceeded(self, mock_send_multicast):
        """Test multicast when quota exceeded"""
        mock_send_multicast.side_effect = messaging.QuotaExceededError("quota")

        with pytest.raises(FCMQuotaExceededError):
            FCMService.send_multicast(
                device_tokens=["t1", "t2"],
                title="Test",
                body="Hello"
            )

    @patch("modules.push_notification.fcm_service.messaging.send_multicast", create=True)
    def test_send_multicast_auth_error(self, mock_send_multicast):
        """Test multicast with auth error"""
        mock_send_multicast.side_effect = messaging.ThirdPartyAuthError("auth")

        with pytest.raises(FCMAuthError):
            FCMService.send_multicast(
                device_tokens=["t1", "t2"],
                title="Test",
                body="Hello"
            )

    @patch("modules.push_notification.fcm_service.messaging.send_multicast", create=True)
    def test_send_multicast_unexpected_error(self, mock_send_multicast):
        """Test multicast with unexpected error"""
        mock_send_multicast.side_effect = Exception("Unexpected")

        with pytest.raises(FCMError) as exc_info:
            FCMService.send_multicast(
                device_tokens=["t1", "t2"],
                title="Test",
                body="Hello"
            )

        assert "Failed to send multicast" in str(exc_info.value)

    # -------------------------
    # TOKEN VALIDATION
    # -------------------------

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_validate_token_success(self, mock_send):
        """Test token validation with valid token"""
        mock_send.return_value = "msg_id"

        assert FCMService.validate_token("valid_token") is True
        
        # Verify dry_run was used
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["dry_run"] is True

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_validate_token_invalid(self, mock_send):
        """Test token validation with invalid token"""
        mock_send.side_effect = messaging.UnregisteredError("bad token")

        assert FCMService.validate_token("bad_token") is False

    @patch("modules.push_notification.fcm_service.messaging.send")
    def test_validate_token_error(self, mock_send):
        """Test token validation with unexpected error"""
        mock_send.side_effect = Exception("Network error")

        assert FCMService.validate_token("token") is False

    # -------------------------
    # SHUTDOWN
    # -------------------------

    @patch("modules.push_notification.fcm_service.firebase_admin.delete_app")
    def test_shutdown_success(self, mock_delete):
        """Test successful FCM shutdown"""
        FCMService._initialized = True
        mock_app = MagicMock()
        FCMService._app = mock_app

        FCMService.shutdown()

        assert FCMService._initialized is False
        assert FCMService._app is None
        mock_delete.assert_called_once_with(mock_app)

    @patch("modules.push_notification.fcm_service.firebase_admin.delete_app")
    def test_shutdown_with_error(self, mock_delete):
        """Test shutdown with error"""
        FCMService._initialized = True
        mock_app = MagicMock()
        FCMService._app = mock_app
        mock_delete.side_effect = Exception("Delete failed")

        # Should not raise, just log error
        FCMService.shutdown()

    def test_shutdown_when_not_initialized(self):
        """Test shutdown when not initialized"""
        FCMService._initialized = False
        FCMService._app = None

        # Should not raise
        FCMService.shutdown()

