from datetime import UTC, datetime
from typing import Optional

from modules.api_key.errors import ApiKeyNotFoundError
from modules.api_key.internal.api_key_util import ApiKeyUtil
from modules.api_key.internal.store.api_key_repository import ApiKeyRepository
from modules.api_key.types import ApiKey, ApiKeyKind, ApiKeyQuery, ApiKeyStatus, ListApiKeysParams
from modules.application.common.types import AuditActor


class ApiKeyReader:
    @staticmethod
    def get_account_keys(*, params: ListApiKeysParams, actor: AuditActor) -> list[ApiKey]:
        # The Settings UI lists only the account's own user-created keys; INTERNAL keys stay hidden.
        return ApiKeyRepository.query(ApiKeyQuery(account_id=params.account_id, kind=ApiKeyKind.USER), actor=actor)

    @staticmethod
    def get_active_by_plaintext(*, plaintext: str, actor: AuditActor) -> Optional[ApiKey]:
        api_key = ApiKeyRepository.query_one(
            ApiKeyQuery(key_hash=ApiKeyUtil.hash_key(plaintext), status=ApiKeyStatus.ACTIVE), actor=actor
        )
        return api_key

    @staticmethod
    def get_owned_key(*, account_id: str, api_key_id: str, actor: AuditActor) -> ApiKey:
        api_key = ApiKeyRepository.query_one(ApiKeyQuery(id=api_key_id, account_id=account_id), actor=actor)
        if api_key is None:
            raise ApiKeyNotFoundError()
        return api_key

    @staticmethod
    def find_expired(*, actor: AuditActor) -> list[ApiKey]:
        return ApiKeyRepository.query(
            ApiKeyQuery(status=ApiKeyStatus.ACTIVE, expires_before=datetime.now(tz=UTC)), actor=actor
        )
