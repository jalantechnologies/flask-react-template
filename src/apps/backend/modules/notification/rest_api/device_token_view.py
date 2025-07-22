from dataclasses import asdict
from typing import cast

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.notification.errors import ValidationError
from modules.notification.notification_service import NotificationService
from modules.notification.types import DeviceType, RegisterDeviceTokenParams, ValidationFailure


class DeviceTokenView(MethodView):
    @access_auth_middleware
    def delete(self) -> ResponseReturnValue:
        account_id = cast(str, getattr(request, "account_id", None))

        deleted_count = NotificationService.delete_account_fcm_tokens_by_account_id(account_id)
        return jsonify({"success": deleted_count > 0, "deleted_count": deleted_count}), 200

    @access_auth_middleware
    def post(self) -> ResponseReturnValue:
        account_id = cast(str, getattr(request, "account_id", None))
        request_data = request.get_json()

        device_type_str = request_data.get("device_type")
        try:
            device_type = DeviceType(device_type_str)
        except (ValueError, TypeError):
            allowed_values = ", ".join([t.value for t in DeviceType])
            raise ValidationError(
                f"Invalid device type: {device_type_str}. Must be one of: {allowed_values}",
                [ValidationFailure(field="device_type", message=f"Must be one of: {allowed_values}")],
            )

        token_params = RegisterDeviceTokenParams(
            account_id=account_id, token=request_data.get("token"), device_type=device_type
        )

        device_token = NotificationService.upsert_account_fcm_token(params=token_params)

        device_token_dict = asdict(device_token)
        device_token_dict["device_type"] = device_token.device_type.value

        return jsonify(device_token_dict), 201
