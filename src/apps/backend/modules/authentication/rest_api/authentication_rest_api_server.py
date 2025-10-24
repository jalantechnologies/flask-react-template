from flask import Blueprint

from modules.authentication.rest_api.authentication_router import AuthenticationRouter


class AuthenticationRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        authentication_api_blueprint = Blueprint("authentication", __name__)
        return AuthenticationRouter.create_route(blueprint=authentication_api_blueprint)
