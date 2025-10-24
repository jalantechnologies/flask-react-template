from flask import Blueprint

from modules.authentication.rest_api.access_token_view import AccessTokenView
from modules.authentication.rest_api.password_reset_token_view import PasswordResetTokenView


class AuthenticationRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule("/access-tokens", view_func=AccessTokenView.as_view("access_token_view"))
        blueprint.add_url_rule(
            "/password-reset-tokens", view_func=PasswordResetTokenView.as_view("password_reset_token_view")
        )
        return blueprint
