import bcrypt


class PasswordHash:
    # The bcrypt hash of a password nobody holds, at the same cost (rounds=10) AccountUtil.hash_password
    # produces for a real password, so verifying against it costs the same as verifying a real one. It
    # guards nothing and can be published; its only job is to make the absent case cost what a real one
    # costs, so an attacker cannot learn which usernames exist from the response time.
    _ABSENT_DIGEST = "$2b$10$lrjOG2MQ/QZO9KF0QYnx7uUOq.mct.XH0KNH03SjtgQsQ/v2lbYOO"

    def __init__(self, digest: str) -> None:
        self._digest = digest

    @classmethod
    def of(cls, digest: str) -> "PasswordHash":
        return cls(digest)

    @classmethod
    def absent(cls) -> "PasswordHash":
        return cls(cls._ABSENT_DIGEST)

    def matches(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self._digest.encode("utf-8"))
