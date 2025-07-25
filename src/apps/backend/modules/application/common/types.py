from dataclasses import dataclass
from enum import Enum
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"

    @property
    def numeric_value(self) -> int:
        return 1 if self == SortDirection.ASC else -1

    @classmethod
    def from_string(cls, value: str) -> "SortDirection":
        value_lower = value.lower()
        if value_lower in ("asc", "ascending", "1"):
            return cls.ASC
        elif value_lower in ("desc", "descending", "-1"):
            return cls.DESC
        else:
            raise ValueError(f"Invalid sort direction: {value}")


@dataclass(frozen=True)
class SortParams:
    sort_by: str
    sort_direction: SortDirection


@dataclass(frozen=True)
class PaginationParams:
    page: int = 1
    size: Optional[int] = None
    offset: int = 0


@dataclass(frozen=True)
class PaginationResult(Generic[T]):
    items: List[T]
    pagination_params: PaginationParams
    total_count: int
    total_pages: int


@dataclass(frozen=True)
class GetPaginatedTasksParams:
    pagination_params: PaginationParams
    sort_params: Optional[SortParams] = None
