from dataclasses import asdict

from flask import jsonify, request
from flask.views import MethodView
from flask.typing import ResponseReturnValue

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.errors import DeviceTokenBadRequestError
from modules.device_token.rest_api.device_token_response_mapper import DeviceTokenResponseMapper

class DeviceTokenView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()
        if not request_data:
            raise DeviceTokenBadRequestError("Request body is required")

        raw_token = request_data.get("device_token")
        raw_platform = request_data.get("platform")

        if not raw_token or not str(raw_token).strip():
            raise DeviceTokenBadRequestError("device_token is required")
            
        if not raw_platform or not str(raw_platform).strip():
            raise DeviceTokenBadRequestError("platform is required")

        registered_token = DeviceTokenService.register_device_token(
            account_id=account_id,
            device_token=str(raw_token).strip(), 
            platform=str(raw_platform).strip(),
            device_info=request_data.get("device_info"),
        )

        response_dto = DeviceTokenResponseMapper.to_register_response(registered_token)
        return jsonify(asdict(response_dto)), 201
    
    @access_auth_middleware
    def get(self, account_id: str) -> ResponseReturnValue:
        device_tokens = DeviceTokenService.get_device_tokens_for_account(account_id=account_id)

        devices = [
            asdict(DeviceTokenResponseMapper.to_list_item(token))
            for token in device_tokens
        ]

        return jsonify({"devices": devices}), 200

    @access_auth_middleware
    def delete(self, account_id: str, device_id: str) -> ResponseReturnValue:
        DeviceTokenService.unregister_device_token(account_id=account_id, device_token_id=device_id)

        return jsonify({"message": "Device unregistered successfully"}), 200
