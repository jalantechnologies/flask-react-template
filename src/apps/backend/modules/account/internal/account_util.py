import bcrypt
from zxcvbn import zxcvbn

from modules.account.errors import AccountPasswordTooWeakError
from modules.config.config_service import ConfigService

MAX_PASSWORD_LENGTH = 128


class AccountUtil:
    @staticmethod
    def hash_password(*, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def compare_password(*, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def validate_password_strength(*, password: str) -> None:
        if len(password) > MAX_PASSWORD_LENGTH:
            raise AccountPasswordTooWeakError(f"Password must be at most {MAX_PASSWORD_LENGTH} characters.")

        minimum_score = ConfigService[int].get_value(key="public.password_policy.min_zxcvbn_score")
        result = zxcvbn(password)
        if result["score"] >= minimum_score:
            return

        feedback = result["feedback"]
        parts = [message for message in [feedback.get("warning"), *feedback.get("suggestions", [])] if message]
        detail = " ".join(parts) if parts else "Please choose a longer, less predictable password."
        raise AccountPasswordTooWeakError(f"This password is too weak. {detail}")
