import enum
import json
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlsplit

DEFAULT_TIMEOUT_SECONDS = 15.0

type HttpHeaders = dict[str, str]
type HttpQueryParams = dict[str, str]
type HttpJsonBody = dict[str, Any]
type HttpFormBody = dict[str, str]


class HttpMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass(frozen=True)
class HttpErrorCode:
    TRANSPORT_FAILURE = "HTTP_ERR_01"
    CONFLICTING_BODY = "HTTP_ERR_02"


@dataclass(frozen=True)
class HttpRequest:
    url: str
    method: HttpMethod = HttpMethod.GET
    headers: HttpHeaders = field(default_factory=dict)
    query_params: HttpQueryParams = field(default_factory=dict)
    json_body: Optional[HttpJsonBody] = None
    form_body: Optional[HttpFormBody] = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    allow_redirects: bool = False

    @property
    def host(self) -> str:
        return urlsplit(self.url).hostname or "unknown-host"

    @property
    def has_conflicting_body(self) -> bool:
        return self.json_body is not None and self.form_body is not None


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: HttpHeaders
    body: str

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        return json.loads(self.body)
