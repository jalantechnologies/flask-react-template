from datetime import datetime, timedelta
from typing import Optional

from bson.errors import InvalidId
from bson.objectid import ObjectId

from modules.push_notification.internal.push_notification_util import PushNotificationUtil
from modules.push_notification.errors import PushNotificationNotFoundError
from modules.push_notification.internal.store.push_notification_repository import PushNotificationRepository
from modules.push_notification.types import CreatePushNotificationParams, PushNotification, NotificationStatus


class PushNotificationWriter:
    @staticmethod
    def create_notification(*, params: CreatePushNotificationParams) -> PushNotification:
        notification_data = {
            "account_id": params.account_id,
            "title": params.title,
            "body": params.body,
            "data": params.data,
            "device_token_ids": [ObjectId(token_id) for token_id in params.device_token_ids],
            "status": NotificationStatus.PENDING.value,
            "priority": params.priority.value,
            "retry_count": 0,
            "max_retries": params.max_retries if params.max_retries is not None else 4,
            "next_retry_at": None,
            "sent_at": None,
            "delivered_at": None,
            "error_message": None,
            "expires_at": params.expires_at,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = PushNotificationRepository.collection().insert_one(notification_data)

        created_bson = PushNotificationRepository.collection().find_one(
            {"_id": result.inserted_id}
        )

        return PushNotificationUtil.convert_push_notification_bson_to_push_notification(created_bson)

    @staticmethod
    def update_status(*, notification_id: str, status: NotificationStatus, error: Optional[str] = None) -> None:
        update_fields = {
            "status": status.value,
            "updated_at": datetime.now()
        }

        if error is not None:
            update_fields["error_message"] = error

        if status == NotificationStatus.SENT:
            update_fields["sent_at"] = datetime.now()
        elif status == NotificationStatus.DELIVERED:
            update_fields["delivered_at"] = datetime.now()

        try:
            object_id = ObjectId(notification_id)
        except InvalidId:
            raise PushNotificationNotFoundError()

        result = PushNotificationRepository.collection().find_one_and_update(
            {"_id": object_id},
            {"$set": update_fields}
        )

        if result is None:
            raise PushNotificationNotFoundError()

        return None

    @staticmethod
    def increment_retry(*, notification_id: str) -> None:
        try:
            object_id = ObjectId(notification_id)
        except InvalidId:
            raise PushNotificationNotFoundError()

        notification_bson = PushNotificationRepository.collection().find_one({"_id": object_id})

        if notification_bson is None:
            raise PushNotificationNotFoundError()

        new_retry_count = notification_bson.get("retry_count", 0) + 1
        max_retries = notification_bson.get("max_retries", 4)

        if new_retry_count >= max_retries:
            result = PushNotificationRepository.collection().find_one_and_update(
                {"_id": object_id},
                {
                    "$set": {
                        "retry_count": new_retry_count,
                        "status": NotificationStatus.EXPIRED.value,
                        "updated_at": datetime.now(),
                        "error_message": "Maximum retry attempts exceeded"
                    }
                }
            )
        else:
            backoff_minutes = 2 ** new_retry_count
            next_retry_at = datetime.now() + timedelta(minutes=backoff_minutes)
            
            result = PushNotificationRepository.collection().find_one_and_update(
                {"_id": object_id},
                {
                    "$set": {
                        "retry_count": new_retry_count,
                        "next_retry_at": next_retry_at,
                        "status": NotificationStatus.FAILED.value,
                        "updated_at": datetime.now()
                    }
                }
            )

    @staticmethod
    def mark_as_sent(*, notification_id: str) -> None:
        try:
            object_id = ObjectId(notification_id)
        except InvalidId:
            raise PushNotificationNotFoundError()

        result = PushNotificationRepository.collection().find_one_and_update(
            {"_id": object_id},
            {
                "$set": {
                    "status": NotificationStatus.SENT.value,
                    "sent_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )

        if result is None:
            raise PushNotificationNotFoundError()

        return None
