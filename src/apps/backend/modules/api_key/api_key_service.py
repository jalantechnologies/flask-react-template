from typing import Optional

from modules.api_key.internal.api_key_reader import ApiKeyReader
from modules.api_key.internal.api_key_util import ApiKeyUtil
from modules.api_key.internal.api_key_writer import ApiKeyWriter
from modules.api_key.types import (
    ApiKey,
    ApiKeyKind,
    AuthenticateApiKeyParams,
    CreateApiKeyParams,
    CreateApiKeyResult,
    ListApiKeysParams,
    RevokeApiKeyParams,
)
from modules.application.common.types import AuditActor

# Internal keys are not owned by a human; their account_id is a sentinel that identifies the app itself.
INTERNAL_ACCOUNT_ID = "system"


class ApiKeyService:
    @staticmethod
    def create_api_key(*, params: CreateApiKeyParams, actor: AuditActor) -> CreateApiKeyResult:
        return ApiKeyWriter.create(params=params, actor=actor)

    @staticmethod
    def create_internal_api_key(*, name: str, actor: AuditActor) -> CreateApiKeyResult:
        return ApiKeyWriter.create(
            params=CreateApiKeyParams(account_id=INTERNAL_ACCOUNT_ID, name=name, kind=ApiKeyKind.INTERNAL), actor=actor
        )

    @staticmethod
    def list_api_keys(*, params: ListApiKeysParams, actor: AuditActor) -> list[ApiKey]:
        return ApiKeyReader.get_account_keys(params=params, actor=actor)

    @staticmethod
    def revoke_api_key(*, params: RevokeApiKeyParams, actor: AuditActor) -> ApiKey:
        return ApiKeyWriter.revoke(params=params, actor=actor)

    @staticmethod
    def is_api_key_credential(credential: str) -> bool:
        # Lets the auth middleware route a Bearer credential to key resolution or JWT verification
        # without reaching into this module's internals.
        return ApiKeyUtil.is_api_key(credential)

    @staticmethod
    def authenticate_api_key(*, params: AuthenticateApiKeyParams, actor: AuditActor) -> Optional[ApiKey]:
        # Resolve a plaintext key to its owning account for the auth middleware. Returns None when the
        # key is unknown or not active; raises ApiKeyExpiredError when a matched key has passed expiry.
        api_key = ApiKeyReader.get_active_by_plaintext(plaintext=params.plaintext_key, actor=actor)
        if api_key is None:
            return None
        return ApiKeyWriter.validate_expiry_and_touch(api_key=api_key, actor=actor)

    @staticmethod
    def expire_expired_keys(*, actor: AuditActor) -> list[ApiKey]:
        expired = ApiKeyReader.find_expired(actor=actor)
        return [ApiKeyWriter.expire_key(api_key_id=key.id, actor=actor) for key in expired]
