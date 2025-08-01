import hashlib
import os
from datetime import datetime, timedelta
from typing import Any

import bcrypt

from modules.authentication.internals.password_reset_token.store.password_reset_token_model import (
    PasswordResetTokenModel,
)
from modules.authentication.types import PasswordResetToken
from modules.config.config_service import ConfigService


class PasswordResetTokenUtil:

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def compare_password(*, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def generate_password_reset_token() -> str:
        return hashlib.sha256(os.urandom(60)).hexdigest()

    @staticmethod
    def hash_password_reset_token(reset_token: str) -> str:
        return bcrypt.hashpw(reset_token.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def get_token_expires_at() -> datetime:
        default_token_expire_time_in_seconds = ConfigService[int].get_value(key="accounts.token_expires_in_seconds")
        return datetime.now() + timedelta(seconds=default_token_expire_time_in_seconds)

    @staticmethod
    def is_token_expired(expires_at: datetime) -> bool:
        return datetime.now() > expires_at

    @staticmethod
    def convert_password_reset_token_bson_to_password_reset_token(
        password_reset_token_bson: dict[str, Any]
    ) -> PasswordResetToken:
        validated_password_reset_token_data = PasswordResetTokenModel.from_bson(password_reset_token_bson)
        return PasswordResetToken(
            account=str(validated_password_reset_token_data.account),
            id=str(validated_password_reset_token_data.id),
            is_used=validated_password_reset_token_data.is_used,
            is_expired=PasswordResetTokenUtil.is_token_expired(validated_password_reset_token_data.expires_at),
            expires_at=str(validated_password_reset_token_data.expires_at),
            token=validated_password_reset_token_data.token,
        )
