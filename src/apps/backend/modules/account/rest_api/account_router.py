from flask import Blueprint

from modules.account.rest_api.account_view import AccountView


class AccountRouter:
    ACCOUNT_BY_ID_URL = "/accounts/<id>"

    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule("/accounts", view_func=AccountView.as_view("account_view"))
        blueprint.add_url_rule(
            AccountRouter.ACCOUNT_BY_ID_URL, view_func=AccountView.as_view("account_view_by_id"), methods=["GET"]
        )
        blueprint.add_url_rule(
            AccountRouter.ACCOUNT_BY_ID_URL, view_func=AccountView.as_view("account_update"), methods=["PATCH"]
        )
        blueprint.add_url_rule(
            AccountRouter.ACCOUNT_BY_ID_URL, view_func=AccountView.as_view("account_delete"), methods=["DELETE"]
        )

        blueprint.add_url_rule(
            "/accounts/<account_id>/notification-preferences",
            view_func=AccountView.update_account_notification_preferences,
            methods=["PATCH"],
        )

        return blueprint
