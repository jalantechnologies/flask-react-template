from flask import Blueprint

from modules.api_key.rest_api.api_key_view import ApiKeyView


class ApiKeyRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule(
            "/accounts/<account_id>/api-keys", view_func=ApiKeyView.as_view("api_key_view"), methods=["POST", "GET"]
        )
        blueprint.add_url_rule(
            "/accounts/<account_id>/api-keys/<api_key_id>",
            view_func=ApiKeyView.as_view("api_key_view_by_id"),
            methods=["DELETE"],
        )
        return blueprint
