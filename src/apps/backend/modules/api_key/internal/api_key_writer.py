from datetime import UTC, datetime, timedelta
from typing import ClassVar, Optional

from modules.api_key.errors import ApiKeyAlreadyRevokedError, ApiKeyExpiredError, ApiKeyNotFoundError
from modules.api_key.internal.api_key_reader import ApiKeyReader
from modules.api_key.internal.api_key_util import ApiKeyUtil
from modules.api_key.internal.store.api_key_repository import ApiKeyRepository
from modules.api_key.types import (
    ApiKey,
    ApiKeyQuery,
    ApiKeyStatus,
    CreateApiKeyParams,
    CreateApiKeyResult,
    RevokeApiKeyParams,
)
from modules.application.common.types import AuditActor


class ApiKeyWriter:
    # A key is touched at most once per window so the auth hot path does not write on every request.
    _LAST_USED_DEBOUNCE_SECONDS: ClassVar[int] = 300

    @staticmethod
    def create(*, params: CreateApiKeyParams, actor: AuditActor) -> CreateApiKeyResult:
        plaintext = ApiKeyUtil.generate_plaintext_key()
        expires_at: Optional[datetime] = None
        if params.expires_in_days is not None:
            expires_at = datetime.now(tz=UTC) + timedelta(days=params.expires_in_days)

        api_key = ApiKey(
            id="",
            account_id=params.account_id,
            name=params.name,
            key_hash=ApiKeyUtil.hash_key(plaintext),
            status=ApiKeyStatus.ACTIVE,
            kind=params.kind,
            expires_at=expires_at,
        )
        created = ApiKeyRepository.create(api_key, actor=actor)
        return CreateApiKeyResult(api_key=created, plaintext_key=plaintext)

    @staticmethod
    def revoke(*, params: RevokeApiKeyParams, actor: AuditActor) -> ApiKey:
        existing = ApiKeyReader.get_owned_key(account_id=params.account_id, api_key_id=params.api_key_id, actor=actor)
        if existing.status == ApiKeyStatus.REVOKED:
            raise ApiKeyAlreadyRevokedError()

        # The write filter re-asserts ownership so the mutation cannot cross an account boundary.
        revoked = ApiKeyRepository.update_by_query(
            ApiKeyQuery(id=params.api_key_id, account_id=params.account_id),
            {"status": ApiKeyStatus.REVOKED.value},
            actor=actor,
        )
        if revoked is None:
            raise ApiKeyNotFoundError()
        return revoked

    @staticmethod
    def expire_key(*, api_key_id: str, actor: AuditActor) -> ApiKey:
        expired = ApiKeyRepository.update(api_key_id, {"status": ApiKeyStatus.EXPIRED.value}, actor=actor)
        if expired is None:
            raise ApiKeyNotFoundError()
        return expired

    @staticmethod
    def validate_expiry_and_touch(*, api_key: ApiKey, actor: AuditActor) -> ApiKey:
        now = datetime.now(tz=UTC)
        if api_key.expires_at is not None and api_key.expires_at < now:
            ApiKeyWriter.expire_key(api_key_id=api_key.id, actor=actor)
            raise ApiKeyExpiredError()

        if (
            api_key.last_used_at is None
            or (now - api_key.last_used_at).total_seconds() > ApiKeyWriter._LAST_USED_DEBOUNCE_SECONDS
        ):
            ApiKeyRepository.update_fields(api_key.id, {"last_used_at": now}, actor=actor)
        return api_key
