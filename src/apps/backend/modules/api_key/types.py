import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from modules.application.common.types import QueryParams
from modules.application.errors import AppError


class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ApiKeyKind(str, enum.Enum):
    # USER keys are created by an account holder in Settings and managed there.
    # INTERNAL keys are system-provisioned for the app's own service-to-service calls; they
    # authenticate like any key but are hidden from the human-facing UI list.
    USER = "user"
    INTERNAL = "internal"


@dataclass(frozen=True)
class ApiKey:
    id: str
    account_id: str
    name: str
    key_hash: str
    status: ApiKeyStatus
    kind: ApiKeyKind
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class ApiKeyQuery(QueryParams):
    id: Optional[str] = None
    account_id: Optional[str] = None
    key_hash: Optional[str] = None
    name: Optional[str] = None
    status: Optional[ApiKeyStatus] = None
    kind: Optional[ApiKeyKind] = None
    expires_before: Optional[datetime] = None


@dataclass(frozen=True)
class CreateApiKeyParams:
    account_id: str
    name: str
    kind: ApiKeyKind = ApiKeyKind.USER
    expires_in_days: Optional[int] = None

    @classmethod
    def from_dict(cls, account_id: str, request_data: Any) -> "CreateApiKeyParams":
        if not isinstance(request_data, dict):
            raise AppError(
                code=ApiKeyErrorCode.BAD_REQUEST, http_status_code=400, message="Request body must be a JSON object"
            )

        name = request_data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise AppError(code=ApiKeyErrorCode.BAD_REQUEST, http_status_code=400, message="name is required")

        expires_in_days = request_data.get("expires_in_days")
        if expires_in_days is not None and (not isinstance(expires_in_days, int) or expires_in_days <= 0):
            raise AppError(
                code=ApiKeyErrorCode.BAD_REQUEST,
                http_status_code=400,
                message="expires_in_days must be a positive integer",
            )

        return cls(account_id=account_id, name=name.strip(), expires_in_days=expires_in_days)


@dataclass(frozen=True)
class ListApiKeysParams:
    account_id: str


@dataclass(frozen=True)
class RevokeApiKeyParams:
    account_id: str
    api_key_id: str


@dataclass(frozen=True)
class AuthenticateApiKeyParams:
    plaintext_key: str


@dataclass(frozen=True)
class CreateApiKeyResult:
    api_key: ApiKey
    plaintext_key: str


@dataclass(frozen=True)
class ApiKeyErrorCode:
    NOT_FOUND: str = "API_KEY_ERR_01"
    BAD_REQUEST: str = "API_KEY_ERR_02"
    ALREADY_REVOKED: str = "API_KEY_ERR_03"
    EXPIRED: str = "API_KEY_ERR_04"
    INVALID: str = "API_KEY_ERR_05"
