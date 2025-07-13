from flask import Blueprint

from modules.account.rest_api.account_view import AccountView
from modules.notification.rest_api.account_notification_preferences_view import AccountNotificationPreferencesView


class AccountRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule("/accounts", view_func=AccountView.as_view("account_view"))
        blueprint.add_url_rule("/accounts/<id>", view_func=AccountView.as_view("account_view_by_id"), methods=["GET"])
        blueprint.add_url_rule("/accounts/<id>", view_func=AccountView.as_view("account_update"), methods=["PATCH"])

        blueprint.add_url_rule(
            "/accounts/<account_id>/notification-preferences",
            view_func=AccountNotificationPreferencesView.as_view("notification_preferences_update"),
            methods=["PUT"],
        )

        return blueprint
