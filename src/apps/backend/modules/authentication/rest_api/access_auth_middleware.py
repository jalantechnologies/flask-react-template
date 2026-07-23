from functools import wraps
from typing import Any, Callable

from flask import request

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


def verify_request_access_token() -> AccessTokenPayload:
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        raise AuthorizationHeaderNotFoundError("Authorization header is missing.")

    authorization_parts = authorization_header.split(" ")
    if len(authorization_parts) != 2 or authorization_parts[0] != "Bearer" or not authorization_parts[1]:
        raise InvalidAuthorizationHeaderError("Invalid authorization header.")

    access_token_payload = AuthenticationService.verify_access_token(token=authorization_parts[1])
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
