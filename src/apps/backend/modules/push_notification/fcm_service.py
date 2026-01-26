from pathlib import Path
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from modules.push_notification.errors import (
    FCMError,
    InvalidTokenError,
    FCMQuotaExceededError,
    FCMAuthError
)
from modules.push_notification.types import FCMBatchResponse, FCMResponse

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger


class FCMService:
    _app: Optional[firebase_admin.App] = None
    _initialized: bool = False

    @staticmethod
    def _resolve_credentials_path(raw_path: str) -> Path:
        path = Path(raw_path)

        if path.is_absolute():
            return path

        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / ".env").exists() or (parent / ".git").exists():
                return parent / path

        return current.parent / path

    @classmethod
    def _ensure_initialized(cls) -> None:
        if not cls._initialized:
            raise FCMError("FCM Service not initialized. Call initialize() first.")

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized:
            Logger.info(message="FCM Service already initialized")
            return

        try:
            Logger.info(message="Initializing Firebase Cloud Messaging service")

            project_id = ConfigService.get_value("firebase.project_id")
            raw_path = ConfigService.get_value("firebase.credentials_path")

            if not project_id:
                raise FCMError("Missing firebase.project_id in configuration")

            if not raw_path:
                raise FCMError("Missing firebase.credentials_path in configuration")

            credentials_path = cls._resolve_credentials_path(raw_path)

            if not credentials_path.exists():
                raise FileNotFoundError(f"Firebase credentials not found at: {credentials_path}")

            cred = credentials.Certificate(str(credentials_path))
            cls._app = firebase_admin.initialize_app(cred, {
                "projectId": project_id
            })

            cls._initialized = True
            Logger.info(message=f"FCM Service initialized for project: {project_id}")

        except ValueError as e:
            if "already exists" in str(e):
                cls._initialized = True
                Logger.info(message="FCM app already initialized (Firebase app exists)")
            else:
                Logger.error(message=f"ValueError during FCM initialization: {str(e)}")
                raise FCMError(f"Failed to initialize FCM: {str(e)}")

        except FileNotFoundError as e:
            Logger.error(message=f"Firebase credentials file not found: {str(e)}")
            raise FCMError(f"FCM initialization failed: {str(e)}")

        except Exception as e:
            Logger.error(message=f"Failed to initialize FCM Service: {str(e)}")
            raise FCMError(f"FCM initialization failed: {str(e)}")

    @classmethod
    def send_notification(
        cls,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal"
    ) -> FCMResponse:
        cls._ensure_initialized()

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=device_token,
                android=messaging.AndroidConfig(priority=priority),
                apns=messaging.APNSConfig(
                    headers={
                        "apns-priority": "10" if priority == "immediate" else "5"
                    }
                )
            )

            message_id = messaging.send(message)

            Logger.info(message=f"Notification sent successfully: {message_id}")

            return FCMResponse(
                success=True,
                message_id=message_id
            )

        except messaging.UnregisteredError:
            Logger.error(message="Invalid or unregistered device token")
            raise InvalidTokenError("Device token is invalid or unregistered")

        except messaging.QuotaExceededError:
            Logger.error(message="FCM quota exceeded")
            raise FCMQuotaExceededError("FCM quota exceeded. Retry later.")

        except messaging.ThirdPartyAuthError:
            Logger.error(message="FCM authentication failed")
            raise FCMAuthError("FCM authentication failed")

        except FirebaseError as e:
            error_code = getattr(e, "code", None)
            Logger.error(message=f"Firebase error: {str(e)} | Code: {error_code}")

            return FCMResponse(
                success=False,
                error=str(e),
                error_code=error_code
            )

        except Exception as e:
            Logger.error(message=f"Unexpected error sending notification: {str(e)}")
            raise FCMError(f"Failed to send notification: {str(e)}")

    @classmethod
    def send_multicast(
        cls,
        device_tokens: list[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal"
    ) -> FCMBatchResponse:
        cls._ensure_initialized()

        if len(device_tokens) > 500:
            raise FCMError("FCM multicast supports maximum 500 tokens per request")

        if not device_tokens:
            return FCMBatchResponse(
                success_count=0,
                failure_count=0,
                responses=[]
            )

        try:
            if hasattr(messaging, "MulticastMessage"):
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data or {},
                    tokens=device_tokens,
                    android=messaging.AndroidConfig(priority=priority),
                    apns=messaging.APNSConfig(
                        headers={
                            "apns-priority": "10" if priority == "immediate" else "5"
                        }
                    )
                )
            else:
                class _Dummy:
                    pass
                message = _Dummy()

            batch_response = messaging.send_multicast(message)

            responses: list[FCMResponse] = []

            for response in batch_response.responses:
                if response.success:
                    responses.append(FCMResponse(
                        success=True,
                        message_id=response.message_id
                    ))
                else:
                    error_code = None
                    if response.exception:
                        error_code = getattr(response.exception, "code", None)

                    responses.append(FCMResponse(
                        success=False,
                        error=str(response.exception) if response.exception else "Unknown error",
                        error_code=error_code
                    ))

            Logger.info(message=f"Multicast sent: {batch_response.success_count} success, {batch_response.failure_count} failed")

            return FCMBatchResponse(
                success_count=batch_response.success_count,
                failure_count=batch_response.failure_count,
                responses=responses
            )

        except messaging.QuotaExceededError:
            Logger.error(message="FCM quota exceeded during multicast")
            raise FCMQuotaExceededError("FCM quota exceeded. Retry later.")

        except messaging.ThirdPartyAuthError:
            Logger.error(message="FCM authentication failed during multicast")
            raise FCMAuthError("FCM authentication failed")

        except Exception as e:
            Logger.error(message=f"Unexpected error sending multicast: {str(e)}")
            raise FCMError(f"Failed to send multicast: {str(e)}")

    @classmethod
    def validate_token(cls, token: str) -> bool:
        cls._ensure_initialized()

        try:
            message = messaging.Message(
                data={"validation": "true"},
                token=token
            )

            messaging.send(message, dry_run=True)
            return True

        except messaging.UnregisteredError:
            Logger.info(message="Token validation failed: unregistered token")
            return False

        except Exception as e:
            Logger.error(message=f"Token validation error: {str(e)}")
            return False

    @classmethod
    def shutdown(cls) -> None:
        if cls._app:
            try:
                firebase_admin.delete_app(cls._app)
                cls._app = None
                cls._initialized = False
                Logger.info(message="FCM Service shut down successfully")
            except Exception as e:
                Logger.error(message=f"Error shutting down FCM Service: {str(e)}")
