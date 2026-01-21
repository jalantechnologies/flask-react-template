from flask import Blueprint

from modules.device_token.rest_api.device_token_router import DeviceTokenRouter


class DeviceTokenRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        device_token_api_blueprint = Blueprint("device_token", __name__)

        return DeviceTokenRouter.create_route(blueprint=device_token_api_blueprint)
