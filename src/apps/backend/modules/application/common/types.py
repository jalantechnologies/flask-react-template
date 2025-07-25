from dataclasses import dataclass
from enum import Enum
from typing import Generic, List, TypeVar

T = TypeVar("T")


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
