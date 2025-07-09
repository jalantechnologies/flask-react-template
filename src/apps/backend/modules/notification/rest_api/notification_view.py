from typing import Dict, List, Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.notification.notification_service import NotificationService
from modules.notification.types import FCMNotificationData, SendFCMParams


class NotificationView(MethodView):
    @access_auth_middleware
    def post(self) -> ResponseReturnValue:
        request_data = request.get_json() or {}

        title: str = request_data.get("title", "")
        body: str = request_data.get("body", "")
        data: Dict[str, str] = request_data.get("data", {})
        image_url: Optional[str] = request_data.get("image_url")

        user_ids: Optional[List[str]] = request_data.get("user_ids")
        tokens: Optional[List[str]] = request_data.get("tokens")
        topic: Optional[str] = request_data.get("topic")

        notification_data = FCMNotificationData(title=title, body=body, data=data, image_url=image_url)

        params = SendFCMParams(notification=notification_data, user_ids=user_ids, tokens=tokens, topic=topic)

        result = NotificationService.send_push_notification(params=params)

        return jsonify({"message": "Notification sent", "results": result}), 200
