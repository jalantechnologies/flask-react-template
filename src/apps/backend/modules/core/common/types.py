import enum
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class QueryParams:
    """Base for a repository's typed query object; subclasses declare optional domain fields that
    `_to_filter` maps to a store filter. A query object is the code equivalent of a query string
    (`AccountQuery(username=x)` is the analogue of `/accounts?username=x`), so reads stay in domain
    language and the store specifics live inside the repository."""


@dataclass(frozen=True)
class NoQuery(QueryParams):
    """Marker for repositories that expose no `query()` — a singleton store or a write-only log that
    is only ever read by id. Declared as the query type: `ApplicationRepository[Entity, NoQuery]`."""


@dataclass(frozen=True)
class PaginationParams:
    page: int
    size: int
    offset: int = 0


class SortDirection(Enum):
    ASC = ("asc", 1)
    DESC = ("desc", -1)

    def __init__(self, string_value: str, numeric_value: int):
        self.string_value = string_value
        self.numeric_value = numeric_value

    @classmethod
    def from_string(cls, value: str) -> "SortDirection":
        for member in cls:
            if member.string_value == value:
                return member
        raise ValueError(f"Invalid sort direction: {value}")


@dataclass(frozen=True)
class SortParams:
    sort_by: str
    sort_direction: SortDirection


@dataclass(frozen=True)
class PaginationResult(Generic[T]):
    items: List[T]
    pagination_params: PaginationParams
    total_count: int
    total_pages: int


UNSET = object()


REDACTED = "[redacted]"

type FieldChangeValue = Optional[str | int | float | bool]


class ResourceAction(str, enum.Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ActorType(str, enum.Enum):
    ACCOUNT = "account"
    JOB = "job"
    WORKER = "worker"
    ANONYMOUS = "anonymous"


class AuditOutcome(str, enum.Enum):
    SUCCESS = "success"
    DENIED = "denied"


@dataclass(frozen=True)
class AuditActor:
    actor_type: ActorType
    actor_id: Optional[str] = None


@dataclass(frozen=True)
class FieldChange:
    old: FieldChangeValue
    new: FieldChangeValue


type FieldChanges = dict[str, FieldChange]


@dataclass(frozen=True)
class AuditRecord:
    resource_type: str
    resource_id: str
    actor_type: ActorType
    actor_id: Optional[str]
    action: ResourceAction
    timestamp: datetime
    changes: FieldChanges = field(default_factory=dict)
    outcome: AuditOutcome = AuditOutcome.SUCCESS


@dataclass(frozen=True)
class AuditLogEntry:
    id: str
    resource_type: str
    resource_id: str
    actor_type: ActorType
    actor_id: Optional[str]
    action: ResourceAction
    timestamp: datetime
    changes: FieldChanges = field(default_factory=dict)
    outcome: AuditOutcome = AuditOutcome.SUCCESS
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


type JobArguments = dict[str, FieldChangeValue]


class JobRunStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class JobRun:
    id: str
    job_name: str
    status: JobRunStatus
    arguments: JobArguments = field(default_factory=dict)
    retry_count: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class JobRunQuery(QueryParams):
    id: Optional[str] = None
    job_name: Optional[str] = None
    status: Optional[JobRunStatus] = None
