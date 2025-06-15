import json
import os
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, messaging

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.errors import NotificationConfigurationError, NotificationServiceError
from modules.notification.types import SendMultipleNotificationsParams, SendNotificationParams


class FirebaseNotificationProvider:
    """
    Firebase Cloud Messaging (FCM) implementation of notification provider

    Handles initialization of Firebase Admin SDK and sending push notifications
    through the Firebase Cloud Messaging service
    """

    _app: Optional[firebase_admin.App] = None
    _initialized: bool = False

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize Firebase Admin SDK with service account credentials

        Credentials are loaded from one of these sources (in priority order):
        1. Service account JSON file in project root
        2. Environment variable containing service account JSON
        3. Configuration service value

        Raises:
            NotificationConfigurationError: If no valid credentials are found
            NotificationServiceError: If initialization fails for other reasons
        """
        if cls._initialized:
            return

        try:
            if os.path.exists("firebase-service-account.json"):
                cred = credentials.Certificate("firebase-service-account.json")
                cls._app = firebase_admin.initialize_app(cred)
                Logger.info(message="Firebase initialized with service account file")

            elif os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON"):
                service_account_info = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON") or "")
                cred = credentials.Certificate(service_account_info)
                cls._app = firebase_admin.initialize_app(cred)
                Logger.info(message="Firebase initialized with environment variables")

            elif ConfigService.has_value("firebase.service_account_json"):
                service_account_json = ConfigService[str].get_value(key="firebase.service_account_json")
                if service_account_json is not None:
                    service_account_info = json.loads(service_account_json)
                    cred = credentials.Certificate(service_account_info)
                    cls._app = firebase_admin.initialize_app(cred)
                    Logger.info(message="Firebase initialized with configuration service")
                else:
                    Logger.error(message="Firebase configuration value is None")
                    raise NotificationConfigurationError()

            else:
                Logger.error(message="Firebase configuration is missing or invalid")
                raise NotificationConfigurationError()

            cls._initialized = True

        except Exception as e:
            Logger.error(message=f"Failed to initialize Firebase: {str(e)}")
            raise NotificationServiceError(str(e))

    @classmethod
    def lazy_initialize(cls) -> None:
        """
        Initialize Firebase only if it hasn't been initialized yet

        This allows components to ensure Firebase is ready without
        knowing the initialization state
        """
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def send_notification(cls, params: SendNotificationParams) -> Dict[str, Any]:
        """
        Send notification to a specific FCM token

        Performs basic validation and handles common FCM error cases
        with appropriate error responses

        Args:
            params: Contains recipient FCM token and notification content

        Returns:
            Response containing success status and message ID or error details
        """
        try:
            cls.lazy_initialize()
        except Exception as e:
            Logger.error(message=f"Firebase initialization failed: {str(e)}")
            return {"success": False, "error": "Firebase initialization failed", "message": str(e)}

        try:
            if not params.recipient.fcm_token or len(params.recipient.fcm_token.strip()) < 10:
                Logger.error(message=f"Invalid FCM token: {params.recipient.fcm_token}")
                return {
                    "success": False,
                    "error": "Invalid FCM token format",
                    "message": "The provided FCM token is invalid",
                }

            notification = messaging.Notification(title=params.content.title, body=params.content.body)

            message = messaging.Message(
                notification=notification,
                data=params.content.data or {},
                token=params.recipient.fcm_token,
                android=messaging.AndroidConfig(
                    ttl=3600,
                    priority="high",
                    notification=messaging.AndroidNotification(
                        icon="stock_ticker_update", color="#f45342", sound="default"
                    ),
                ),
                apns=messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(badge=1, sound="default"))),
            )

            response = messaging.send(message)
            Logger.info(message=f"Successfully sent notification: {response}")

            return {"success": True, "message_id": response, "message": "Notification sent successfully"}

        except messaging.InvalidArgumentError as e:
            Logger.error(message=f"Invalid argument error: {str(e)}")
            return {"success": False, "error": "Invalid FCM token or message format", "message": str(e)}

        except messaging.UnregisteredError as e:
            Logger.error(message=f"Unregistered token error: {str(e)}")
            return {"success": False, "error": "FCM token is not registered or expired", "message": str(e)}

        except Exception as e:
            Logger.error(message=f"Failed to send notification: {str(e)}")
            return {"success": False, "error": "Internal server error", "message": str(e)}

    @classmethod
    def _validate_tokens(cls, tokens: List[str]) -> tuple[List[str], List[str]]:
        """
        Validate a list of FCM tokens and separate valid from invalid ones

        Args:
            tokens: List of FCM tokens to validate

        Returns:
            Tuple of (valid_tokens, invalid_tokens)
        """
        valid_tokens = []
        invalid_tokens = []

        for token in tokens:
            if not token or len(token.strip()) < 10:
                Logger.warning(message=f"Invalid FCM token format: {token}")
                invalid_tokens.append(token)
            else:
                valid_tokens.append(token)

        return valid_tokens, invalid_tokens

    @classmethod
    def _create_notification_configs(
        cls, title: str, body: str
    ) -> tuple[messaging.Notification, messaging.AndroidConfig, messaging.APNSConfig]:
        """
        Create common notification configurations

        Args:
            title: Notification title
            body: Notification body

        Returns:
            Tuple of (notification, android_config, apns_config)
        """
        notification = messaging.Notification(title=title, body=body)

        android_config = messaging.AndroidConfig(
            ttl=3600,
            priority="high",
            notification=messaging.AndroidNotification(icon="stock_ticker_update", color="#f45342", sound="default"),
        )

        apns_config = messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(badge=1, sound="default")))

        return notification, android_config, apns_config

    @classmethod
    def _send_to_token(
        cls,
        token: str,
        notification: messaging.Notification,
        data: Dict[str, str],
        android_config: messaging.AndroidConfig,
        apns_config: messaging.APNSConfig,
    ) -> Dict[str, Any]:
        """
        Send notification to a single token and handle errors

        Args:
            token: FCM token to send to
            notification: Prepared notification object
            data: Custom data to include
            android_config: Android specific configuration
            apns_config: APNS specific configuration

        Returns:
            Dict with result info for this token
        """
        try:
            message = messaging.Message(
                notification=notification, data=data or {}, token=token, android=android_config, apns=apns_config
            )

            response = messaging.send(message)
            Logger.info(message=f"Successfully sent notification to token {token[:15]}...: {response}")

            return {"token": token, "success": True, "message_id": response}

        except messaging.InvalidArgumentError as e:
            Logger.error(message=f"Invalid argument error for token {token[:15]}...: {str(e)}")
            return {"token": token, "success": False, "error": "Invalid FCM token or message format", "message": str(e)}

        except messaging.UnregisteredError as e:
            Logger.error(message=f"Unregistered token error for token {token[:15]}...: {str(e)}")
            return {
                "token": token,
                "success": False,
                "error": "FCM token is not registered or expired",
                "message": str(e),
            }

        except Exception as e:
            Logger.error(message=f"Failed to send notification to token {token[:15]}...: {str(e)}")
            return {"token": token, "success": False, "error": "Internal server error", "message": str(e)}

    @classmethod
    def send_multiple_notifications(cls, params: SendMultipleNotificationsParams) -> Dict[str, Any]:
        """
        Send the same notification to multiple FCM tokens

        Performs basic validation and handles common FCM error cases
        with appropriate error responses. Will attempt to send to all tokens
        even if some fail.

        Args:
            params: Contains list of recipient FCM tokens and notification content

        Returns:
            Response containing success status, succeeded and failed tokens details
        """
        try:
            cls.lazy_initialize()
        except Exception as e:
            Logger.error(message=f"Firebase initialization failed: {str(e)}")
            return {"success": False, "error": "Firebase initialization failed", "message": str(e)}

        if not params.recipients.fcm_tokens or len(params.recipients.fcm_tokens) == 0:
            Logger.error(message="No FCM tokens provided")
            return {
                "success": False,
                "error": "No FCM tokens provided",
                "message": "At least one FCM token must be provided",
            }

        valid_tokens, invalid_tokens = cls._validate_tokens(params.recipients.fcm_tokens)

        if not valid_tokens:
            Logger.error(message="All provided FCM tokens are invalid")
            return {
                "success": False,
                "error": "All FCM tokens are invalid",
                "message": "All provided FCM tokens have invalid format",
                "invalid_tokens": invalid_tokens,
            }

        results = {
            "success": True,
            "total_tokens": len(params.recipients.fcm_tokens),
            "successful_tokens": 0,
            "failed_tokens": 0,
            "token_results": [],
        }

        notification, android_config, apns_config = cls._create_notification_configs(
            params.content.title, params.content.body
        )

        for token in valid_tokens:
            token_result = cls._send_to_token(
                token, notification, params.content.data or {}, android_config, apns_config
            )

            results["token_results"].append(token_result)

            if token_result["success"]:
                results["successful_tokens"] += 1
            else:
                results["failed_tokens"] += 1

        if results["successful_tokens"] == 0:
            results["success"] = False
            results["error"] = "All notifications failed to send"

        if invalid_tokens:
            results["invalid_tokens"] = invalid_tokens

        return results
