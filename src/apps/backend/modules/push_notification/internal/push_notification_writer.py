from datetime import datetime
from typing import Optional

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pymongo import ReturnDocument

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
        created_bson = PushNotificationRepository.collection().find_one({"_id": result.inserted_id})

        if created_bson is None:
            raise PushNotificationNotFoundError()

        return PushNotificationUtil.convert_push_notification_bson_to_push_notification(created_bson)

    @staticmethod
    def update_status(*, notification_id: str, status: NotificationStatus, error: Optional[str] = None) -> PushNotification:
        current_time = datetime.now()

        update_fields = {
            "status": status.value,
            "updated_at": current_time
        }

        if error is not None:
            update_fields["error_message"] = error
        elif status in {NotificationStatus.SENT, NotificationStatus.DELIVERED, NotificationStatus.PROCESSING}:
            update_fields["error_message"] = None

        if status == NotificationStatus.SENT:
            update_fields["sent_at"] = current_time
            update_fields["next_retry_at"] = None
        elif status == NotificationStatus.DELIVERED:
            update_fields["delivered_at"] = current_time
            update_fields["next_retry_at"] = None

        try:
            object_id = ObjectId(notification_id)
        except InvalidId:
            raise PushNotificationNotFoundError()

        result = PushNotificationRepository.collection().find_one_and_update(
            {"_id": object_id},
            {"$set": update_fields},
            return_document=ReturnDocument.AFTER
        )

        if result is None:
            raise PushNotificationNotFoundError()

        return PushNotificationUtil.convert_push_notification_bson_to_push_notification(result)

    @staticmethod
    def increment_retry(*, notification_id: str) -> None:
        current_time = datetime.now()

        try:
            object_id = ObjectId(notification_id)
        except InvalidId:
            raise PushNotificationNotFoundError()

        updated_notification = PushNotificationRepository.collection().find_one_and_update(
            {"_id": object_id},
            [
                {"$set": {"retry_count": {"$add": ["$retry_count", 1]}}},
                {"$set": {
                    "status": {"$cond": [{"$gte": ["$retry_count", "$max_retries"]}, NotificationStatus.EXPIRED.value, NotificationStatus.FAILED.value]},
                    "next_retry_at": {"$cond": [
                        {"$gte": ["$retry_count", "$max_retries"]},
                        None,
                        {"$add": [current_time, {"$multiply": [{"$pow": [2, "$retry_count"]}, 60000]}]}
                    ]},
                    "error_message": {"$cond": [{"$gte": ["$retry_count", "$max_retries"]}, "Maximum retry attempts exceeded", "$error_message"]},
                    "updated_at": current_time
                }}
            ],
            return_document=ReturnDocument.AFTER
        )

        if updated_notification is None:
            raise PushNotificationNotFoundError()
