from flask import Blueprint

from modules.device_token.rest_api.device_token_view import DeviceTokenView


class DeviceTokenRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule(
            "/accounts/<account_id>/devices",
            view_func=DeviceTokenView.as_view("device_token_view"),
            methods=["POST", "GET"],
        )

        blueprint.add_url_rule(
            "/accounts/<account_id>/devices/<device_id>",
            view_func=DeviceTokenView.as_view("device_token_view_by_id"),
            methods=["DELETE", "PATCH"],
        )

        return blueprint
