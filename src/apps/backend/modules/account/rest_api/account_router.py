from flask import Blueprint

from modules.account.rest_api.account_view import AccountView


class AccountRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule("/accounts", view_func=AccountView.as_view("account_view"))
        blueprint.add_url_rule("/accounts/<id>", view_func=AccountView.as_view("account_view_by_id"), methods=["GET"])
        blueprint.add_url_rule("/accounts/<id>", view_func=AccountView.as_view("account_update"), methods=["PATCH"])
        blueprint.add_url_rule("/accounts/<id>", view_func=AccountView.as_view("account_delete"), methods=["DELETE"])
        return blueprint
