from dataclasses import dataclass
from datetime import datetime

from modules.application.common.types import PaginationParams, SortParams


@dataclass(frozen=True)
class Comment:
    id: str
    account_id: str
    task_id: str
    content: str


@dataclass(frozen=True)
class GetCommentParams:
    account_id: str
    task_id: str
    comment_id: str


@dataclass(frozen=True)
class GetPaginatedCommentParams:
    account_id: str
    task_id: str
    pagination_params: PaginationParams
    sort_params: SortParams | None = None


@dataclass(frozen=True)
class CreateCommentParams:
    account_id: str
    task_id: str
    content: str

    def to_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "task_id": self.task_id,
            "content": self.content,
        }


@dataclass(frozen=True)
class UpdateCommentParams:
    account_id: str
    task_id: str
    comment_id: str
    content: str


@dataclass(frozen=True)
class DeleteCommentParams:
    account_id: str
    task_id: str
    comment_id: str


@dataclass(frozen=True)
class CommentDeletionResult:
    comment_id: str
    deleted_at: datetime
    success: bool


@dataclass(frozen=True)
class CommentErrorCode:
    NOT_FOUND: str = "COMMENT_ERR_01"
    BAD_REQUEST: str = "COMMENT_ERR_02"
