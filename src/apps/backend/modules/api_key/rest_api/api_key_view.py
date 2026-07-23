from typing import Any, Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.api_key.api_key_service import ApiKeyService
from modules.api_key.types import ApiKey, CreateApiKeyParams, ListApiKeysParams, RevokeApiKeyParams
from modules.application.common.types import ActorType, AuditActor
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware


def _serialize_api_key(api_key: ApiKey, *, plaintext_key: Optional[str] = None) -> dict[str, Any]:
    # The stored hash and the internal `kind` are never exposed; the plaintext is returned once, only on
    # create, and never persisted in a readable form.
    payload: dict[str, Any] = {
        "id": api_key.id,
        "account_id": api_key.account_id,
        "name": api_key.name,
        "status": api_key.status.value,
        "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
        "last_used_at": (api_key.last_used_at.isoformat() if api_key.last_used_at else None),
    }
    if plaintext_key is not None:
        payload["key"] = plaintext_key
    return payload


class ApiKeyView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str) -> ResponseReturnValue:
        params = CreateApiKeyParams.from_dict(account_id, request.get_json(silent=True))
        result = ApiKeyService.create_api_key(
            params=params, actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=account_id)
        )
        return (jsonify(_serialize_api_key(result.api_key, plaintext_key=result.plaintext_key)), 201)

    @access_auth_middleware
    def get(self, account_id: str) -> ResponseReturnValue:
        api_keys = ApiKeyService.list_api_keys(
            params=ListApiKeysParams(account_id=account_id),
            actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=account_id),
        )
        return (jsonify({"items": [_serialize_api_key(api_key) for api_key in api_keys]}), 200)

    @access_auth_middleware
    def delete(self, account_id: str, api_key_id: str) -> ResponseReturnValue:
        ApiKeyService.revoke_api_key(
            params=RevokeApiKeyParams(account_id=account_id, api_key_id=api_key_id),
            actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=account_id),
        )
        return "", 204
