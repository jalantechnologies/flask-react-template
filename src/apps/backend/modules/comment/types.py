from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modules.application.common.types import PaginationParams, PaginationResult, SortParams


@dataclass(frozen=True)
class Comment:
    id: str
    task_id: str
    account_id: str
    author_name: str
    content: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateCommentParams:
    task_id: str
    account_id: str
    content: str


@dataclass(frozen=True)
class UpdateCommentParams:
    comment_id: str
    task_id: str
    account_id: str
    content: str


@dataclass(frozen=True)
class GetCommentParams:
    comment_id: str
    task_id: str
    account_id: str


@dataclass(frozen=True)
class GetPaginatedCommentsParams:
    task_id: str
    account_id: str
    pagination_params: PaginationParams
    sort_params: Optional[SortParams] = None


@dataclass(frozen=True)
class DeleteCommentParams:
    comment_id: str
    task_id: str
    account_id: str


@dataclass(frozen=True)
class CommentDeletionResult:
    comment_id: str
    deleted_at: datetime
    success: bool


@dataclass(frozen=True)
class CommentErrorCode:
    NOT_FOUND: str = "COMMENT_ERR_01"
    BAD_REQUEST: str = "COMMENT_ERR_02"
    UNAUTHORIZED: str = "COMMENT_ERR_03"