from dataclasses import asdict
from typing import cast

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams


class DeviceTokenView(MethodView):
    @access_auth_middleware
    def post(self) -> ResponseReturnValue:
        account_id = cast(str, getattr(request, "account_id", None))
        request_data = request.get_json()

        token_params = RegisterDeviceTokenParams(
            user_id=account_id, token=request_data.get("token"), device_type=request_data.get("device_type")
        )

        device_token = NotificationService.upsert_user_fcm_token(params=token_params)

        return jsonify(asdict(device_token)), 201
