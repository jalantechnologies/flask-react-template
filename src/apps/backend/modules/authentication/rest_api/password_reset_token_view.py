from dataclasses import asdict

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreatePasswordResetTokenParams


class PasswordResetTokenView(MethodView):
    def post(self) -> ResponseReturnValue:
        request_data = request.get_json()
        password_reset_token_params = CreatePasswordResetTokenParams(**request_data)
        password_reset_token = AuthenticationService.create_password_reset_token(params=password_reset_token_params)
        password_reset_token_dict = asdict(password_reset_token)
        return jsonify(password_reset_token_dict), 201
