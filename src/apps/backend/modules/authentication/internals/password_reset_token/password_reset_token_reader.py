from modules.account.errors import AccountBadRequestError
from modules.authentication.errors import PasswordResetTokenNotFoundError
from modules.authentication.internals.password_reset_token.password_reset_token_util import PasswordResetTokenUtil
from modules.authentication.internals.password_reset_token.store.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from modules.authentication.types import PasswordResetToken, PasswordResetTokenQuery


class PasswordResetTokenReader:
    @staticmethod
    def get_password_reset_token_by_account_id(account_id: str) -> PasswordResetToken:
        # The repository orders by expires_at desc, so this returns the account's most recent token.
        password_reset_token = PasswordResetTokenRepository.query_one(PasswordResetTokenQuery(account_id=account_id))

        if password_reset_token is None:
            raise PasswordResetTokenNotFoundError()

        return password_reset_token

    @staticmethod
    def verify_password_reset_token(account_id: str, token: str) -> PasswordResetToken:
        password_reset_token = PasswordResetTokenReader.get_password_reset_token_by_account_id(account_id)

        if password_reset_token.is_expired:
            raise AccountBadRequestError(
                f"Password reset link is expired for accountId {account_id}. Please retry with new link"
            )
        if password_reset_token.is_used:
            raise AccountBadRequestError(
                f"Password reset is already used for accountId {account_id}. Please retry with new link"
            )

        is_token_valid = PasswordResetTokenUtil.compare_password(
            password=token, hashed_password=password_reset_token.token
        )
        if not is_token_valid:
            raise AccountBadRequestError(
                f"Password reset link is invalid for accountId {account_id}. Please retry with new link."
            )

        return password_reset_token
