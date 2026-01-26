from datetime import datetime, timedelta
from typing import Optional, List

from modules.logger.logger import Logger
from modules.config.config_service import ConfigService
from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.types import GetDeviceTokensParams
from modules.push_notification.fcm_service import FCMService
from modules.push_notification.internal.push_notification_reader import PushNotificationReader
from modules.push_notification.internal.push_notification_writer import PushNotificationWriter
from modules.push_notification.errors import (
    InvalidTokenError,
    FCMQuotaExceededError,
    FCMAuthError,
)
from modules.push_notification.types import (
    PushNotification,
    CreatePushNotificationParams,
    Priority,
    NotificationStatus,
    GetPendingNotificationsParams,
    GetNotificationsByAccountIdParams,
    NotificationResult,
)


class PushNotificationService:
    @staticmethod
    def send_notification(
        *,
        account_id: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal",
        max_retries: Optional[int] = None,
    ) -> Optional[PushNotification]:
        try:
            try:
                priority_enum = Priority(priority)
            except ValueError:
                from modules.push_notification.errors import InvalidPriorityError
                raise InvalidPriorityError(priority)

            Logger.info(
                message=(
                    f"Sending {priority} priority notification | "
                    f"account_id={account_id} | "
                    f"title={title}"
                )
            )

            device_tokens_response = DeviceTokenService.get_device_tokens_for_account(
                params=GetDeviceTokensParams(account_id=account_id)
            )

            if not device_tokens_response:
                Logger.warn(
                    message=f"No active devices found for account {account_id}"
                )
                return None

            device_token_ids = [token.id for token in device_tokens_response]

            params = CreatePushNotificationParams(
                account_id=account_id,
                title=title,
                body=body,
                device_token_ids=device_token_ids,
                priority=priority_enum,
                data=data,
                max_retries=max_retries,
                expires_at=PushNotificationService._calculate_expiry_time(),
            )

            notification = PushNotificationWriter.create_notification(params=params)

            if priority_enum == Priority.IMMEDIATE:
                PushNotificationService._send_immediate(
                    notification=notification,
                    device_tokens=device_tokens_response,
                )
                refreshed = PushNotificationReader.get_notification_by_id(notification.id)
                if refreshed:
                    notification = refreshed

            return notification

        except (InvalidTokenError, FCMQuotaExceededError, FCMAuthError) as e:
            Logger.error(message=f"FCM error sending notification: {str(e)}")
            raise

    @staticmethod
    def send_to_user(
        *,
        user_id: str,
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal",
    ) -> NotificationResult:
        try:
            response = FCMService.send_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data,
                priority=priority,
            )

            return NotificationResult(
                success=response.success,
                message_id=response.message_id,
                error=response.error,
            )
        except InvalidTokenError as exc:
            Logger.error(message=f"Invalid token for user {user_id}: {str(exc)}")
            return NotificationResult(
                success=False,
                error=str(exc),
                invalid_tokens=[device_token],
            )
        except Exception as exc:
            Logger.error(message=f"Failed to send notification to user {user_id}: {str(exc)}")
            return NotificationResult(success=False, error=str(exc))

    @staticmethod
    def send_to_multiple_users(
        *,
        user_tokens: dict[str, str],
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal",
    ) -> NotificationResult:
        try:
            if not user_tokens:
                Logger.warn(message="No device tokens provided for multicast send")
                return NotificationResult(success=False, error="No device tokens provided")

            tokens = list(user_tokens.values())
            batch_response = FCMService.send_multicast(
                device_tokens=tokens,
                title=title,
                body=body,
                data=data,
                priority=priority,
            )

            invalid_tokens: list[str] = []
            invalid_codes = {"registration-token-not-registered", "invalid-registration-token"}

            for token, response in zip(tokens, batch_response.responses):
                if not response.success and (response.error_code in invalid_codes):
                    invalid_tokens.append(token)

            success = batch_response.success_count > 0

            return NotificationResult(
                success=success,
                error=None if success else "Failed to send to all device tokens",
                invalid_tokens=invalid_tokens,
            )

        except InvalidTokenError as exc:
            Logger.error(message=f"Invalid token in multicast send: {str(exc)}")
            return NotificationResult(success=False, error=str(exc))
        except Exception as exc:
            Logger.error(message=f"Failed to send multicast notification: {str(exc)}")
            return NotificationResult(success=False, error=str(exc))

    @staticmethod
    def send_to_devices(
        *,
        device_token_ids: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
        priority: str = "normal",
    ) -> Optional[PushNotification]:
        try:
            try:
                priority_enum = Priority(priority)
            except ValueError:
                from modules.push_notification.errors import InvalidPriorityError
                raise InvalidPriorityError(priority)

            if not device_token_ids:
                Logger.warn(message="No device tokens provided")
                return None

            from modules.device_token.internal.device_token_reader import DeviceTokenReader
            
            device_tokens = DeviceTokenReader.get_device_tokens_by_ids(
                device_token_ids=device_token_ids
            )

            if not device_tokens:
                Logger.warn(
                    message=(
                        f"No active device tokens found | "
                        f"requested_count={len(device_token_ids)}"
                    )
                )
                return None

            account_id = device_tokens[0].account_id

            Logger.info(
                message=(
                    f"Sending to specific devices | "
                    f"account_id={account_id} | "
                    f"count={len(device_tokens)} | "
                    f"priority={priority}"
                )
            )

            params = CreatePushNotificationParams(
                account_id=account_id,
                title=title,
                body=body,
                device_token_ids=device_token_ids,
                priority=priority_enum,
                data=data,
                expires_at=PushNotificationService._calculate_expiry_time(),
            )

            notification = PushNotificationWriter.create_notification(params=params)

            if priority_enum == Priority.IMMEDIATE:
                PushNotificationWriter.update_status(
                    notification_id=notification.id,
                    status=NotificationStatus.PROCESSING,
                )

                fcm_tokens = [t.device_token for t in device_tokens]
                if not fcm_tokens:
                    PushNotificationWriter.update_status(
                        notification_id=notification.id,
                        status=NotificationStatus.FAILED,
                        error="No active device tokens available",
                    )
                else:
                    success_any = False
                    last_error: Optional[str] = None
                    for tok in fcm_tokens:
                        try:
                            resp = FCMService.send_notification(
                                device_token=tok,
                                title=notification.title,
                                body=notification.body,
                                data=notification.data,
                                priority="immediate",
                            )
                            if resp.success:
                                success_any = True
                            else:
                                last_error = resp.error
                        except InvalidTokenError as e:
                            last_error = str(e)
                        except FCMQuotaExceededError as e:
                            last_error = "FCM quota exceeded"
                        except FCMAuthError as e:
                            last_error = "FCM authentication error"
                        except Exception as e:
                            last_error = str(e)

                    if success_any:
                        PushNotificationWriter.update_status(
                            notification_id=notification.id,
                            status=NotificationStatus.SENT,
                        )
                    else:
                        PushNotificationWriter.update_status(
                            notification_id=notification.id,
                            status=NotificationStatus.FAILED,
                            error=last_error or "Failed to send to devices",
                        )

                refreshed = PushNotificationReader.get_notification_by_id(notification.id)
                if refreshed:
                    notification = refreshed

            return notification

        except Exception as e:
            Logger.error(message=f"Error sending to devices: {str(e)}")
            raise

    @staticmethod
    def get_notification_status(*, notification_id: str) -> Optional[PushNotification]:
        try:
            notification = PushNotificationReader.get_notification_by_id(notification_id)

            if notification:
                Logger.info(
                    message=(
                        f"Notification status | "
                        f"notification_id={notification_id} | "
                        f"status={notification.status.value}"
                    )
                )

            return notification

        except Exception as e:
            Logger.error(message=f"Error getting notification status: {str(e)}")
            raise

    @staticmethod
    def get_pending_notifications(
        *, limit: int = 100, skip: int = 0
    ) -> List[PushNotification]:
        try:
            params = GetPendingNotificationsParams(limit=limit, skip=skip)
            notifications = PushNotificationReader.get_pending_notifications(params=params)

            Logger.info(
                message=f"Retrieved {len(notifications)} pending notifications"
            )

            return notifications

        except Exception as e:
            Logger.error(message=f"Error getting pending notifications: {str(e)}")
            raise

    @staticmethod
    def get_account_notifications(
        *, account_id: str, limit: int = 50, skip: int = 0
    ) -> List[PushNotification]:
        try:
            params = GetNotificationsByAccountIdParams(
                account_id=account_id, limit=limit, skip=skip
            )
            notifications = PushNotificationReader.get_notifications_by_account_id(params=params)

            Logger.info(
                message=(
                    f"Retrieved {len(notifications)} notifications "
                    f"for account {account_id}"
                )
            )

            return notifications

        except Exception as e:
            Logger.error(message=f"Error getting account notifications: {str(e)}")
            raise

    @staticmethod
    def _send_immediate(
        notification: PushNotification, device_tokens: List
    ) -> None:
        try:
            PushNotificationWriter.update_status(
                notification_id=notification.id,
                status=NotificationStatus.PROCESSING,
            )

            fcm_tokens = [token.device_token for token in device_tokens]

            if not fcm_tokens:
                PushNotificationWriter.update_status(
                    notification_id=notification.id,
                    status=NotificationStatus.FAILED,
                    error="No active device tokens available",
                )
                return

            if len(fcm_tokens) == 1:
                response = FCMService.send_notification(
                    device_token=fcm_tokens[0],
                    title=notification.title,
                    body=notification.body,
                    data=notification.data,
                    priority="immediate",
                )

                if response.success:
                    PushNotificationWriter.update_status(
                        notification_id=notification.id,
                        status=NotificationStatus.SENT,
                    )
                else:
                    PushNotificationWriter.update_status(
                        notification_id=notification.id,
                        status=NotificationStatus.FAILED,
                        error=response.error,
                    )
            else:
                batch_response = FCMService.send_multicast(
                    device_tokens=fcm_tokens,
                    title=notification.title,
                    body=notification.body,
                    data=notification.data,
                    priority="immediate",
                )

                if batch_response.success_count > 0:
                    PushNotificationWriter.update_status(
                        notification_id=notification.id,
                        status=NotificationStatus.SENT,
                    )
                else:
                    PushNotificationWriter.update_status(
                        notification_id=notification.id,
                        status=NotificationStatus.FAILED,
                        error=f"Failed to send to any device: {batch_response.failure_count} failures",
                    )

        except InvalidTokenError as e:
            PushNotificationWriter.update_status(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                error=str(e),
            )
            Logger.error(message=f"Invalid token in immediate send: {str(e)}")
        except FCMQuotaExceededError as e:
            PushNotificationWriter.update_status(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                error="FCM quota exceeded",
            )
            Logger.error(message=f"FCM quota exceeded: {str(e)}")
        except FCMAuthError as e:
            PushNotificationWriter.update_status(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                error="FCM authentication error",
            )
            Logger.error(message=f"FCM auth error: {str(e)}")
        except Exception as e:
            PushNotificationWriter.update_status(
                notification_id=notification.id,
                status=NotificationStatus.FAILED,
                error=str(e),
            )
            Logger.error(message=f"Error in immediate send: {str(e)}")

    @staticmethod
    def _calculate_expiry_time() -> datetime:
        try:
            expiry_hours = ConfigService.get_value("push_notification.expiry_hours")
            if expiry_hours is None:
                expiry_hours = 24
        except Exception:
            expiry_hours = 24

        return datetime.now() + timedelta(hours=int(expiry_hours))
