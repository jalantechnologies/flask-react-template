from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreatePasswordResetTokenParams
from modules.core.common.types import ActorType, AuditActor

ANONYMOUS_ACTOR = AuditActor(actor_type=ActorType.ANONYMOUS, actor_id=None)
PASSWORD_RESET_REQUESTED_MESSAGE = "If an account exists for that email, a reset link has been sent."


class PasswordResetTokenView(MethodView):
    def post(self) -> ResponseReturnValue:
        request_data = request.get_json()
        password_reset_token_params = CreatePasswordResetTokenParams(**request_data)
        account = AccountService.get_account_by_username_optional(
            username=password_reset_token_params.username, actor=ANONYMOUS_ACTOR
        )
        if account is not None:
            AuthenticationService.create_password_reset_token(params=account, actor=ANONYMOUS_ACTOR)

        return jsonify({"message": PASSWORD_RESET_REQUESTED_MESSAGE}), 200
