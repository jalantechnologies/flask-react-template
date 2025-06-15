from typing import Any, Dict

from modules.logger.logger import Logger
from modules.notification.internal.firebase_notification_provider import FirebaseNotificationProvider
from modules.notification.types import SendMultipleNotificationsParams, SendNotificationParams


class NotificationService:
    """
    Service responsible for sending notifications to end-users.
    Acts as a facade to abstract different notification providers implementation details.
    """

    _initialized = False

    @staticmethod
    def send_notification(*, params: SendNotificationParams) -> Dict[str, Any]:
        """
        Sends a notification to a specific recipient.

        This method abstracts the underlying notification provider (Firebase)
        to maintain a consistent interface if additional providers are added later.

        Args:
            params: Contains recipient information and notification content

        Returns:
            Response containing success status and message ID or error details
        """
        try:
            return FirebaseNotificationProvider.send_notification(params)
        except Exception as e:
            Logger.error(message=f"Error in notification service: {str(e)}")
            return {"success": False, "error": "Notification service error", "message": str(e)}

    @staticmethod
    def initialize() -> bool:
        """
        Initializes the notification service and its providers.

        Should be called during application startup to ensure the
        notification infrastructure is ready before handling requests.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            FirebaseNotificationProvider.initialize()
            NotificationService._initialized = True
            return True
        except Exception as e:
            Logger.error(message=f"Failed to initialize notification service: {str(e)}")
            return False

    @classmethod
    def send_multiple_notifications(cls, params: SendMultipleNotificationsParams) -> Dict[str, Any]:
        """
        Send the same notification to multiple devices

        Args:
            params: Parameters for sending notifications to multiple recipients

        Returns:
            Dict containing success status and details of succeeded/failed tokens
        """
        return FirebaseNotificationProvider.send_multiple_notifications(params=params)
