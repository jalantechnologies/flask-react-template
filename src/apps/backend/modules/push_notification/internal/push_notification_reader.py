from datetime import datetime
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from modules.push_notification.types import (
    PushNotification,
    NotificationStatus,
    GetPendingNotificationsParams,
    GetRetryNotificationsParams,
    GetNotificationsByAccountIdParams,
)
from modules.push_notification.internal.push_notification_util import PushNotificationUtil
from modules.push_notification.internal.store.push_notification_repository import PushNotificationRepository


class PushNotificationReader:
    @staticmethod
    def get_pending_notifications(*, params: GetPendingNotificationsParams) -> list[PushNotification]:
        notifications_bson = list(
            PushNotificationRepository.collection().find(
                {"status": NotificationStatus.PENDING.value}
            )
            .sort([("priority", -1), ("created_at", 1)])
            .skip(params.skip)
            .limit(params.limit)
        )

        return [
            PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)
            for notification_bson in notifications_bson
        ]

    @staticmethod
    def get_notifications_for_retry(*, params: GetRetryNotificationsParams) -> list[PushNotification]:
        current_time = datetime.now()
        
        notifications_bson = list(
            PushNotificationRepository.collection().find({
                "status": NotificationStatus.FAILED.value,
                "next_retry_at": {"$lte": current_time},
                "$expr": {"$lt": ["$retry_count", "$max_retries"]}
            })
            .sort([("priority", -1), ("next_retry_at", 1)])
            .skip(params.skip)
            .limit(params.limit)
        )

        return [
            PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)
            for notification_bson in notifications_bson
        ]

    @staticmethod
    def get_notification_by_id(notification_id: str) -> Optional[PushNotification]:
        try:
            object_id = ObjectId(notification_id)
        except InvalidId:
            return None

        notification_bson = PushNotificationRepository.collection().find_one(
            {"_id": object_id}
        )

        if not notification_bson:
            return None

        return PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)

    @staticmethod
    def get_notifications_by_account_id(*, params: GetNotificationsByAccountIdParams) -> list[PushNotification]:
        notifications_bson = list(
            PushNotificationRepository.collection().find(
                {"account_id": params.account_id}
            )
            .sort([("created_at", -1)])
            .skip(params.skip)
            .limit(params.limit)
        )

        return [
            PushNotificationUtil.convert_push_notification_bson_to_push_notification(notification_bson)
            for notification_bson in notifications_bson
        ]
