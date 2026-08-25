import bcrypt


class AccountUtil:
    @staticmethod
    def hash_password(*, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def compare_password(*, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def average_password_length(*, passwords: list[str]) -> float:
        # Returns the mean character length across the given passwords.
        return sum(len(password) for password in passwords) / len(passwords)
