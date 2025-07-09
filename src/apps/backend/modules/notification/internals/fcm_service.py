import json
from typing import Any, Dict, List

import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.notification.errors import FCMServiceError, InvalidFCMTokenError
from modules.notification.internals.device_token_reader import DeviceTokenReader
from modules.notification.internals.device_token_writer import DeviceTokenWriter
from modules.notification.types import FCMNotificationData, SendFCMParams


class FCMService:
    _app = None

    @staticmethod
    def _initialize_app() -> None:
        """Initialize Firebase Admin SDK if not already initialized"""
        if FCMService._app is not None:
            return

        try:
            FCMService._validate_firebase_config()
            service_account_json = ConfigService[str].get_value(key="firebase.service_account_key")
            cred_dict = FCMService._parse_service_account(service_account_json)
            FCMService._create_firebase_app(cred_dict)

        except FCMServiceError:
            raise
        except Exception as e:
            Logger.error(message=f"Failed to initialize Firebase Admin SDK: {str(e)}")
            raise FCMServiceError(f"Failed to initialize Firebase Admin SDK: {str(e)}")

    @staticmethod
    def _validate_firebase_config() -> None:
        """Validate Firebase configuration"""
        firebase_enabled = ConfigService[bool].get_value(key="firebase.enabled", default=False)
        if not firebase_enabled:
            Logger.warn(message="Firebase is disabled. FCM notifications will not be sent.")
            raise FCMServiceError("Firebase is disabled in configuration")

    @staticmethod
    def _parse_service_account(service_account_json: str) -> Dict[str, Any]:
        """Parse and validate service account JSON"""
        if not service_account_json or service_account_json.strip() == "":
            raise FCMServiceError("Firebase service account key is not configured")

        try:
            cred_dict: Dict[str, Any] = json.loads(service_account_json)
        except json.JSONDecodeError as e:
            raise FCMServiceError(f"Invalid Firebase service account JSON: {str(e)}")

        # Validate required fields
        required_fields = ["type", "project_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if field not in cred_dict]

        if missing_fields:
            raise FCMServiceError(f"Missing required fields in service account JSON: {missing_fields}")

        if cred_dict.get("type") != "service_account":
            raise FCMServiceError("Service account type must be 'service_account'")

        return cred_dict

    @staticmethod
    def _create_firebase_app(cred_dict: Dict[str, Any]) -> None:
        """Create Firebase app with credentials"""
        cred = credentials.Certificate(cred_dict)
        FCMService._app = firebase_admin.initialize_app(cred)
        Logger.info(message=f"Firebase Admin SDK initialized successfully for project: {cred_dict.get('project_id')}")

    @staticmethod
    def send_notification(params: SendFCMParams) -> Dict[str, int]:
        """Send FCM notifications based on the provided parameters"""
        try:
            FCMService._initialize_app()
        except FCMServiceError as e:
            Logger.error(message=f"FCM initialization failed: {str(e)}")
            return {"successful": 0, "failed": 0}

        if not params.tokens and not params.user_ids and not params.topic:
            raise ValueError("Either tokens, user_ids, or topic must be provided")

        # Handle topic notifications
        if params.topic:
            success = FCMService._send_to_topic(params.notification, params.topic)
            return {"successful": 1 if success else 0, "failed": 0 if success else 1}

        # Get tokens for notification
        tokens = FCMService._collect_tokens(params)
        if not tokens:
            Logger.warn(message="No tokens found for FCM notification")
            return {"successful": 0, "failed": 0}

        return FCMService._send_individual_messages(params.notification, tokens)

    @staticmethod
    def _collect_tokens(params: SendFCMParams) -> List[str]:
        """Collect tokens from params"""
        if params.tokens:
            return params.tokens

        tokens: List[str] = []
        if params.user_ids:
            for user_id in params.user_ids:
                user_tokens = DeviceTokenReader.get_tokens_by_user_id(user_id)
                tokens.extend(user_tokens)

        return tokens

    @staticmethod
    def _send_individual_messages(notification: FCMNotificationData, tokens: List[str]) -> Dict[str, int]:
        """Send individual messages to tokens"""
        successful = 0
        failed = 0
        failed_tokens: List[str] = []

        Logger.info(message=f"Sending {len(tokens)} individual FCM messages")

        for token in tokens:
            if FCMService._send_single_message(notification, token):
                successful += 1
            else:
                failed += 1
                failed_tokens.append(token)

        # Clean up failed tokens
        FCMService._handle_failed_tokens(failed_tokens)

        Logger.info(message=f"FCM individual sends completed: {successful} successful, {failed} failed")
        return {"successful": successful, "failed": failed}

    @staticmethod
    def _send_single_message(notification: FCMNotificationData, token: str) -> bool:
        """Send a single FCM message"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title, body=notification.body, image=notification.image_url
                ),
                data=notification.data,
                token=token,
            )

            response = messaging.send(message)
            Logger.debug(message=f"FCM message sent successfully: {response}")
            return True

        except FirebaseError as e:
            Logger.warn(message=f"FCM send failed for token {token[:20]}...: {str(e)}")
            return False
        except Exception as e:
            Logger.error(message=f"Unexpected error sending to token {token[:20]}...: {str(e)}")
            return False

    @staticmethod
    def _send_to_topic(notification: FCMNotificationData, topic: str) -> bool:
        """Send a notification to a topic"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.title, body=notification.body, image=notification.image_url
            ),
            data=notification.data,
            topic=topic,
        )

        try:
            response = messaging.send(message)
            Logger.info(message=f"FCM topic message sent successfully: {response}")
            return True

        except FirebaseError as e:
            error_code = getattr(e, "code", "unknown")
            Logger.error(message=f"FCM topic request failed [{error_code}]: {str(e)}")
            raise FCMServiceError(f"Failed to send notification to topic {topic}: {str(e)}")
        except Exception as e:
            Logger.error(message=f"Unexpected FCM topic error: {str(e)}")
            raise FCMServiceError(f"Failed to send notification to topic {topic}: {str(e)}")

    @staticmethod
    def _handle_failed_tokens(failed_tokens: List[str]) -> None:
        """Handle failed tokens by removing them from the database"""
        for token in failed_tokens:
            try:
                DeviceTokenWriter.remove_device_token(token)
                Logger.info(message=f"Removed invalid FCM token: {token[:20]}...")
            except Exception as e:
                Logger.error(message=f"Failed to remove invalid token: {str(e)}")

    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate a FCM token by sending a silent notification"""
        try:
            FCMService._initialize_app()
        except FCMServiceError:
            return False

        message = messaging.Message(data={"type": "token_validation"}, token=token)

        try:
            messaging.send(message, dry_run=True)
            return True

        except FirebaseError as e:
            error_code = getattr(e, "code", "unknown")
            Logger.warn(message=f"FCM token validation failed [{error_code}]: {str(e)}")
            raise InvalidFCMTokenError(f"Invalid FCM token: {str(e)}")
        except Exception as e:
            Logger.error(message=f"FCM token validation error: {str(e)}")
            raise InvalidFCMTokenError(f"Token validation failed: {str(e)}")

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Perform a health check on the FCM service"""
        try:
            FCMService._initialize_app()
            return {"status": "healthy", "firebase_initialized": True, "message": "FCM service is operational"}
        except FCMServiceError as e:
            return {
                "status": "unhealthy",
                "firebase_initialized": False,
                "error": str(e),
                "message": "FCM service configuration error",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "firebase_initialized": False,
                "error": str(e),
                "message": "Unexpected FCM service error",
            }
