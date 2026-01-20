from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.push_notification.types import PushNotification, NotificationStatus
from modules.push_notification.internal.push_notification_util import PushNotificationUtil
from modules.push_notification.internal.store.push_notification_repository import PushNotificationRepository


class PushNotificationReader:
    @staticmethod
    def get_pending_notifications(limit: int = 100) -> list[PushNotification]:
        notifications_bson = list(
            PushNotificationRepository.collection().find(
                {"status": NotificationStatus.PENDING.value}
            )
            .sort([("priority", -1), ("created_at", 1)])
            .limit(limit)
        )

        return [
            PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)
            for notification_bson in notifications_bson
        ]

    @staticmethod
    def get_notifications_for_retry() -> list[PushNotification]:
        current_time = datetime.now()
        
        notifications_bson = list(
            PushNotificationRepository.collection().find({
                "status": NotificationStatus.FAILED.value,
                "next_retry_at": {"$lte": current_time},
                "$expr": {"$lt": ["$retry_count", "$max_retries"]}
            })
            .sort([("priority", -1), ("next_retry_at", 1)])
        )

        return [
            PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)
            for notification_bson in notifications_bson
        ]

    @staticmethod
    def get_notification_by_id(notification_id: str) -> Optional[PushNotification]:
        notification_bson = PushNotificationRepository.collection().find_one(
            {"_id": ObjectId(notification_id)}
        )

        if not notification_bson:
            return None

        return PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)

    @staticmethod
    def get_notifications_by_account_id(account_id: str) -> list[PushNotification]:
        notifications_bson = list(
            PushNotificationRepository.collection().find(
                {"account_id": account_id}
            )
            .sort([("created_at", -1)])
        )

        return [
            PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)
            for notification_bson in notifications_bson
        ]
