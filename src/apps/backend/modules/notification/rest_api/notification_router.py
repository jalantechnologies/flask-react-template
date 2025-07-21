from flask import Blueprint

from modules.notification.rest_api.device_token_view import DeviceTokenView


class NotificationRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule("/device-tokens", view_func=DeviceTokenView.as_view("device_token_view"))
        return blueprint
