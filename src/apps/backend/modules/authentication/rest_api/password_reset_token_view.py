from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.account.types import Account
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreatePasswordResetTokenParams
from modules.core.common.types import ActorType, AuditActor
from modules.core.logger.logger import Logger

ANONYMOUS_ACTOR = AuditActor(actor_type=ActorType.ANONYMOUS, actor_id=None)
PASSWORD_RESET_REQUESTED_MESSAGE = "If an account exists for that email, a reset link has been sent."
PROGRAMMING_ERRORS = (AttributeError, ImportError, IndexError, KeyError, NameError, TypeError)


class PasswordResetTokenView(MethodView):
    def post(self) -> ResponseReturnValue:
        request_data = request.get_json()
        password_reset_token_params = CreatePasswordResetTokenParams(**request_data)
        account = AccountService.get_account_by_username_optional(
            username=password_reset_token_params.username, actor=ANONYMOUS_ACTOR
        )
        if account is not None:
            PasswordResetTokenView._request_password_reset_email(account)

        return jsonify({"message": PASSWORD_RESET_REQUESTED_MESSAGE}), 200

    @staticmethod
    def _request_password_reset_email(account: Account) -> None:
        try:
            AuthenticationService.create_password_reset_token(params=account, actor=ANONYMOUS_ACTOR)
        except PROGRAMMING_ERRORS:
            raise
        except Exception as exc:
            Logger.error(
                message=f"password reset token creation failed for account {account.id}: {type(exc).__name__}: {exc}"
            )
