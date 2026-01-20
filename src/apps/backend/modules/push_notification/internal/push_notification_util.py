from typing import Any
from datetime import datetime

from modules.push_notification.types import PushNotification, NotificationStatus, Priority
from modules.push_notification.internal.store.push_notification_model import PushNotificationModel


class PushNotificationUtil:
    @staticmethod
    def convert_push_notification_bson_to_push_notification(push_notification_bson: dict[str, Any]) -> PushNotification:
        validated_push_notification_data = PushNotificationModel.from_bson(push_notification_bson)
        return PushNotification(
            id=str(validated_push_notification_data.id),
            account_id=validated_push_notification_data.account_id,
            title=validated_push_notification_data.title,
            body=validated_push_notification_data.body,
            data=validated_push_notification_data.data,
            device_token_ids=[str(token_id) for token_id in validated_push_notification_data.device_token_ids],
            status=NotificationStatus(validated_push_notification_data.status),
            priority=Priority(validated_push_notification_data.priority),
            retry_count=validated_push_notification_data.retry_count,
            max_retries=validated_push_notification_data.max_retries,
            next_retry_at=validated_push_notification_data.next_retry_at,
            sent_at=validated_push_notification_data.sent_at,
            delivered_at=validated_push_notification_data.delivered_at,
            error_message=validated_push_notification_data.error_message,
            expires_at=validated_push_notification_data.expires_at,
            created_at=validated_push_notification_data.created_at or datetime.now(),
            updated_at=validated_push_notification_data.updated_at or datetime.now()
        )
