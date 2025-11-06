from flask import Blueprint

from modules.authentication.rest_api.authentication_view import SignupView, LoginView
from modules.authentication.rest_api.access_token_view import AccessTokenView
from modules.authentication.rest_api.password_reset_token_view import PasswordResetTokenView


class AuthenticationRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:

        # Signup & Login
        blueprint.add_url_rule(
            "/auth/signup",
            view_func=SignupView.as_view("signup_view"),
            methods=["POST"]
        )
        blueprint.add_url_rule(
            "/auth/login",
            view_func=LoginView.as_view("login_view"),
            methods=["POST"]
        )

        # Existing Token Routes
        blueprint.add_url_rule("/access-tokens", view_func=AccessTokenView.as_view("access_token_view"))
        blueprint.add_url_rule("/password-reset-tokens", view_func=PasswordResetTokenView.as_view("password_reset_token_view"))

        return blueprint