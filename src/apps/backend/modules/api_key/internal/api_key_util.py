import hashlib
import os


class ApiKeyUtil:
    _KEY_PREFIX = "frt_"

    @staticmethod
    def generate_plaintext_key() -> str:
        # The prefix lets the auth middleware tell an API key from a JWT session token without a lookup.
        return ApiKeyUtil._KEY_PREFIX + os.urandom(32).hex()

    @staticmethod
    def is_api_key(candidate: str) -> bool:
        return candidate.startswith(ApiKeyUtil._KEY_PREFIX)

    @staticmethod
    def hash_key(plaintext: str) -> str:
        # SHA-256 over a high-entropy random secret: the stored value is a one-way digest, and lookup is
        # an exact-match on the hash, so no per-key salt is needed the way a low-entropy password would.
        return hashlib.sha256(plaintext.encode()).hexdigest()
