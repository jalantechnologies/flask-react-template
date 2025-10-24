from flask import Blueprint

from modules.account.rest_api.account_router import AccountRouter


class AccountRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        account_api_blueprint = Blueprint("account", __name__)
        return AccountRouter.create_route(blueprint=account_api_blueprint)
