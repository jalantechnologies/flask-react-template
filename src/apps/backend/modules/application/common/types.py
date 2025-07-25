from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationParams:
    page: int
    size: int


@dataclass(frozen=True)
class PaginationResult(Generic[T]):
    items: List[T]
    pagination_params: PaginationParams
    total_count: int
    total_pages: int
