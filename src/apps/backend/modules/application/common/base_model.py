from dataclasses import asdict, dataclass
from typing import Any, Optional, Tuple

from pymongo.cursor import Cursor

from modules.application.common.types import PaginationParams, SortParams


@dataclass
class BaseModel:
    def to_bson(self) -> dict[str, Any]:
        data = asdict(self)
        if data.get("id") is not None:
            data["_id"] = data.pop("id")
        else:
            data.pop("id", None)
        return data

    @staticmethod
    def calculate_pagination_values(
        pagination_params: PaginationParams, total_count: int
    ) -> Tuple[PaginationParams, int, int]:
        page = pagination_params.page
        size = pagination_params.size
        offset = pagination_params.offset

        skip = (page - 1) * size + offset

        total_pages = (total_count + size - 1) // size if size > 0 else 0

        return pagination_params, skip, total_pages

    @staticmethod
    def apply_sort_params(cursor: Cursor, sort_params: Optional[SortParams]) -> Cursor:
        if sort_params:
            return cursor.sort(
                [
                    (sort_params.sort_by, sort_params.sort_direction.numeric_value),
                    ("_id", sort_params.sort_direction.numeric_value),
                ]
            )
        return cursor
