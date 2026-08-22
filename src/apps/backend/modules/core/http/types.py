import enum
import json
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlsplit

from modules.core.http.errors import HttpInvalidJsonBodyError

DEFAULT_TIMEOUT_SECONDS = 15.0
ALLOWED_SCHEMES = frozenset({"http", "https"})
UNKNOWN_HOST = "unknown-host"

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
class HttpRequest:
    url: str
    method: HttpMethod = HttpMethod.GET
    headers: HttpHeaders = field(default_factory=dict)
    query_params: HttpQueryParams = field(default_factory=dict)
    json_body: Optional[HttpJsonBody] = None
    form_body: Optional[HttpFormBody] = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    allow_redirects: bool = False
    allow_internal_target: bool = False

    @property
    def scheme(self) -> str:
        try:
            return urlsplit(self.url).scheme.lower()
        except ValueError:
            return ""

    @property
    def host(self) -> str:
        try:
            return urlsplit(self.url).hostname or UNKNOWN_HOST
        except ValueError:
            return UNKNOWN_HOST

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
        try:
            return json.loads(self.body)
        except json.JSONDecodeError as err:
            raise HttpInvalidJsonBodyError(status_code=self.status_code) from err
