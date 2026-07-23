from flask import Blueprint

from modules.api_key.rest_api.api_key_router import ApiKeyRouter


class ApiKeyRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        api_key_blueprint = Blueprint("api_key", __name__)
        return ApiKeyRouter.create_route(blueprint=api_key_blueprint)
