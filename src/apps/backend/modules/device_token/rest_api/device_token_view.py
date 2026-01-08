from dataclasses import asdict

from flask import jsonify, request
from flask.views import MethodView
from flask.typing import ResponseReturnValue

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.errors import DeviceTokenBadRequestError, InvalidPlatformError
from modules.device_token.rest_api.device_token_response_mapper import DeviceTokenResponseMapper
from modules.device_token.types import UpdateDeviceTokenParams, CreateDeviceTokenParams, GetDeviceTokensParams, DeleteDeviceTokenParams, Platform


class DeviceTokenView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()
        if not request_data:
            raise DeviceTokenBadRequestError("Request body is required.")

        raw_token = request_data.get("device_token")
        raw_platform = request_data.get("platform")
        device_info = request_data.get("device_info")

        if not raw_token or not str(raw_token).strip():
            raise DeviceTokenBadRequestError("Device token is required.")
            
        if not raw_platform or not str(raw_platform).strip():
            raise DeviceTokenBadRequestError("Platform is required.")
        
        if device_info is not None and not isinstance(device_info, dict):
            raise DeviceTokenBadRequestError("Device info must be an object.")
        
        try:
            platform_enum = Platform(str(raw_platform).strip().lower())
        except ValueError:
            raise InvalidPlatformError(str(raw_platform))

        create_device_token_params = CreateDeviceTokenParams(
            account_id=account_id,
            device_token=str(raw_token).strip(),
            platform=platform_enum,
            device_info=device_info,
        )

        created_token = DeviceTokenService.create_device_token(params=create_device_token_params)

        response_dto = DeviceTokenResponseMapper.to_register_response(created_token)
        return jsonify(asdict(response_dto)), 201
    
    @access_auth_middleware
    def get(self, account_id: str) -> ResponseReturnValue:
        get_device_token_params = GetDeviceTokensParams(
            account_id=account_id
        )

        device_tokens = DeviceTokenService.get_device_tokens_for_account(params=get_device_token_params)

        devices = [
            asdict(DeviceTokenResponseMapper.to_list_item(token))
            for token in device_tokens
        ]

        return jsonify({"devices": devices}), 200
    
    @access_auth_middleware
    def patch(self, account_id: str, device_id: str) -> ResponseReturnValue:
        request_data = request.get_json(silent=True) or {}

        ALLOWED_FIELDS = {"device_token", "device_info"}
        unexpected = set(request_data.keys()) - ALLOWED_FIELDS
        if unexpected:
            raise DeviceTokenBadRequestError(
                f"Unsupported fields in PATCH: {', '.join(unexpected)}."
            )

        raw_device_token = request_data.get("device_token")
        device_info = request_data.get("device_info")

        if raw_device_token is not None:
            stripped_token = str(raw_device_token).strip()
            if not stripped_token:
                raise DeviceTokenBadRequestError("Device token cannot be empty.")
        else:
            stripped_token = None
        
        if device_info is not None and not isinstance(device_info, dict):
            raise DeviceTokenBadRequestError("Device info must be an object.")

        update_device_token_params = UpdateDeviceTokenParams(
            account_id=account_id,
            device_token_id=device_id,
            device_token=stripped_token,
            device_info=device_info,
        )

        updated_token = DeviceTokenService.update_device_token(params=update_device_token_params)

        response_dto = DeviceTokenResponseMapper.to_update_response(updated_token)
        return jsonify(asdict(response_dto)), 200

    @access_auth_middleware
    def delete(self, account_id: str, device_id: str) -> ResponseReturnValue:
        delete_device_token_params = DeleteDeviceTokenParams(
            account_id=account_id,
            device_token_id=device_id
        )
        
        DeviceTokenService.deactivate_device_token(params=delete_device_token_params)

        return '', 204
