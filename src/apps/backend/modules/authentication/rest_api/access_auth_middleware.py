from functools import wraps
from typing import Any, Callable

from flask import request

from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.errors import (
    AuthorizationHeaderNotFoundError,
    InvalidAuthorizationHeaderError,
    UnauthorizedAccessError,
)
from modules.authentication.types import AccessTokenPayload


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
        raise UnauthorizedAccessError("Unauthorized access.")


def access_auth_middleware(next_function: Callable) -> Callable:
    @wraps(next_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if "account_id" in kwargs:
            enforce_account_ownership(kwargs["account_id"])
        else:
            verify_request_access_token()

        return next_function(*args, **kwargs)

    return wrapper
