from flask import Blueprint

from modules.account.rest_api.account_view import AccountView


class AccountRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule("/accounts", methods=["POST"], view_func=AccountView.as_view("account_view"))
        blueprint.add_url_rule(
            "/accounts/<account_id>",
            methods=["DELETE", "GET", "PATCH"],
            view_func=AccountView.as_view("account_view_by_id"),
        )

        blueprint.add_url_rule(
            "/accounts/<account_id>/notification-preferences",
            methods=["PATCH"],
            view_func=AccountView.update_account_notification_preferences,
        )

        return blueprint
