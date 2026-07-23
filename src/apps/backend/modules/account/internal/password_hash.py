import bcrypt


class PasswordHash:
    _TIMING_EQUALIZING_DIGEST_FOR_ABSENT_ACCOUNT = "$2b$10$lrjOG2MQ/QZO9KF0QYnx7uUOq.mct.XH0KNH03SjtgQsQ/v2lbYOO"

    def __init__(self, digest: str) -> None:
        self._digest = digest

    @classmethod
    def of(cls, digest: str) -> "PasswordHash":
        return cls(digest)

    @classmethod
    def for_absent_account_with_equalized_timing(cls) -> "PasswordHash":
        return cls(cls._TIMING_EQUALIZING_DIGEST_FOR_ABSENT_ACCOUNT)

    def matches(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self._digest.encode("utf-8"))
