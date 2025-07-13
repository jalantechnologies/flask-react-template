from dataclasses import asdict

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.notification.errors import ValidationError
from modules.notification.types import NotificationPreferencesParams
from modules.notification.notification_service import NotificationService


class AccountNotificationPreferencesView(MethodView):
    @access_auth_middleware
    def put(self, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if not request_data:
            raise ValidationError("Request body is required")

        for field in ["email_enabled", "push_enabled", "sms_enabled"]:
            if field in request_data and not isinstance(request_data[field], bool):
                raise ValidationError(f"{field} must be a boolean")

        preferences = NotificationPreferencesParams(
            email_enabled=request_data.get("email_enabled", True),
            push_enabled=request_data.get("push_enabled", True),
            sms_enabled=request_data.get("sms_enabled", True),
        )

        updated_preferences = NotificationService.create_or_update_account_notification_preferences(
            account_id=account_id, preferences=preferences
        )
        return jsonify(asdict(updated_preferences)), 200
