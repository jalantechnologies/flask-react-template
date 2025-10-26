from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modules.application.common.types import PaginationParams, SortParams


@dataclass(frozen=True)
class Comment:
    id: str
    account_id: str
    task_id: str
    text: str


@dataclass(frozen=True)
class GetTaskParams:
    account_id: str
    task_id: str


@dataclass(frozen=True)
class GetCommentParams:
    account_id: str
    task_id: str
    comment_id: str


@dataclass(frozen=True)
class GetPaginatedCommentsParams:
    account_id: str
    pagination_params: PaginationParams
    sort_params: Optional[SortParams] = None


@dataclass(frozen=True)
class CreateCommentParams:
    account_id: str
    text: str
    task_id: str


@dataclass(frozen=True)
class UpdateCommentParams:
    account_id: str
    task_id: str
    comment_id: str
    text: str


@dataclass(frozen=True)
class DeleteCommentParams:
    account_id: str
    task_id: str
    comment_id: str


@dataclass(frozen=True)
class CommentDeletionResult:
    task_id: str
    deleted_at: datetime
    comment_id: str
    success: bool


@dataclass(frozen=True)
class TaskErrorCode:
    NOT_FOUND: str = "TASK_ERR_01"
    BAD_REQUEST: str = "TASK_ERR_02"
