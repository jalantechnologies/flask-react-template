from functools import wraps
from typing import Any, Callable

from flask import request

from modules.api_key.api_key_service import ApiKeyService
from modules.api_key.types import AuthenticateApiKeyParams
from modules.application.application_service import ApplicationService
from modules.application.common.types import ActorType, AuditActor, AuditOutcome, ResourceAction
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.errors import (
    AuthorizationHeaderNotFoundError,
    InvalidAuthorizationHeaderError,
    UnauthorizedAccessError,
)
from modules.authentication.types import AccessTokenPayload

# The account boundary is the only resource the middleware can name for every route without importing
# each module's collection: a denied attempt is recorded against the owner boundary the caller crossed.
DENIED_RESOURCE_TYPE = "accounts"

# The API-key lookup runs before any identity is proven, so its reads and its last-used/expiry writes
# are attributed to an anonymous actor, exactly like the pre-auth login flows.
ANONYMOUS_ACTOR = AuditActor(actor_type=ActorType.ANONYMOUS, actor_id=None)


def _resolve_api_key(plaintext: str) -> AccessTokenPayload:
    api_key = ApiKeyService.authenticate_api_key(
        params=AuthenticateApiKeyParams(plaintext_key=plaintext), actor=ANONYMOUS_ACTOR
    )
    if api_key is None:
        raise InvalidAuthorizationHeaderError("Invalid API key.")
    setattr(request, "account_id", api_key.account_id)
    return AccessTokenPayload(account_id=api_key.account_id)


def verify_request_access_token() -> AccessTokenPayload:
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        raise AuthorizationHeaderNotFoundError("Authorization header is missing.")

    authorization_parts = authorization_header.split(" ")
    if len(authorization_parts) != 2 or authorization_parts[0] != "Bearer" or not authorization_parts[1]:
        raise InvalidAuthorizationHeaderError("Invalid authorization header.")

    credential = authorization_parts[1]
    # An API key carries a distinguishing prefix, so a non-interactive caller and a session token share
    # the same Bearer scheme without ambiguity or a lookup to tell them apart.
    if ApiKeyService.is_api_key_credential(credential):
        return _resolve_api_key(credential)

    access_token_payload = AuthenticationService.verify_access_token(token=credential)
    setattr(request, "account_id", access_token_payload.account_id)
    return access_token_payload


def enforce_account_ownership(account_id: str) -> None:
    access_token_payload = verify_request_access_token()
    if access_token_payload.account_id != account_id:
        ApplicationService.record_audit(
            actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=access_token_payload.account_id),
            resource_type=DENIED_RESOURCE_TYPE,
            resource_id=account_id,
            action=ResourceAction.READ,
            outcome=AuditOutcome.DENIED,
        )
        raise UnauthorizedAccessError("Unauthorized access.")


def access_auth_middleware(next_function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(next_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if "account_id" in kwargs:
            enforce_account_ownership(kwargs["account_id"])
        else:
            verify_request_access_token()

        return next_function(*args, **kwargs)

    return wrapper
