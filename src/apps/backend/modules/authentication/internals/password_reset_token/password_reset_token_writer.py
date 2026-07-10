from datetime import UTC, datetime

from modules.authentication.errors import PasswordResetTokenNotFoundError
from modules.authentication.internals.password_reset_token.password_reset_token_util import PasswordResetTokenUtil
from modules.authentication.internals.password_reset_token.store.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from modules.authentication.types import PasswordResetToken


class PasswordResetTokenWriter:
    @staticmethod
    def create_password_reset_token(account_id: str, token: str) -> PasswordResetToken:
        token_hash = PasswordResetTokenUtil.hash_password_reset_token(token)
        expires_at = PasswordResetTokenUtil.get_token_expires_at()

        return PasswordResetTokenRepository.create_for_account(
            account_id=account_id, token_hash=token_hash, expires_at=expires_at
        )

    @staticmethod
    def set_password_reset_token_as_used(password_reset_token_id: str) -> PasswordResetToken:
        updated_token = PasswordResetTokenRepository.update(
            password_reset_token_id, {"is_used": True, "updated_at": datetime.now(UTC)}
        )
        if updated_token is None:
            raise PasswordResetTokenNotFoundError()

        return updated_token
