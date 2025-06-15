from flask import Blueprint

from modules.notification.rest_api.fcm_token_view import FCMTokenView
from modules.notification.rest_api.notification_view import NotificationView


class NotificationRouter:
    """Routes HTTP requests to the appropriate notification view handlers"""

    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        """
        Registers notification endpoints with the provided blueprint
        """
        notification_view = NotificationView.as_view("notification_view")
        blueprint.add_url_rule("/notifications", view_func=notification_view, methods=["POST"])

        multiple_notification_view = NotificationView.as_view("multiple_notification_view")
        blueprint.add_url_rule("/notifications/multiple", view_func=multiple_notification_view, methods=["POST"])

        fcm_token_view = FCMTokenView.as_view("fcm_token_view")
        blueprint.add_url_rule("/fcm-tokens", view_func=fcm_token_view, methods=["GET", "POST", "DELETE"])

        return blueprint
