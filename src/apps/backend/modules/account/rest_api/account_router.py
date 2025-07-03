from typing import Final

from flask import Blueprint

from modules.account.rest_api.account_view import AccountView


class AccountRouter:
    ACCOUNTS_ROUTE: Final[str] = "/accounts"
    ACCOUNT_BY_ID_ROUTE: Final[str] = "/accounts/<id>"

    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:

        blueprint.add_url_rule(
            rule=AccountRouter.ACCOUNTS_ROUTE,
            endpoint="create_account",
            view_func=AccountView.as_view("create_account"),
            methods=["POST"],
        )

        blueprint.add_url_rule(
            rule=AccountRouter.ACCOUNT_BY_ID_ROUTE,
            endpoint="account_by_id",
            view_func=AccountView.as_view("account_by_id"),
            methods=["GET", "PATCH", "DELETE"],
        )

        return blueprint
