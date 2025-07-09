from dataclasses import asdict

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.notification.types import UpdateNotificationPreferencesParams


class NotificationPreferencesView(MethodView):
    @access_auth_middleware
    def put(self, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        update_params = UpdateNotificationPreferencesParams(
            account_id=account_id,
            email_enabled=request_data.get("email_enabled", True),
            push_enabled=request_data.get("push_enabled", True),
            sms_enabled=request_data.get("sms_enabled", True),
        )

        preferences = AccountService.update_notification_preferences(params=update_params)
        return jsonify(asdict(preferences)), 200
