from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modules.application.common.types import PaginationParams, SortParams


@dataclass
class Comment:
    id: str
    task_id: str
    account_id: str
    content: str
    author_name: str
    active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class CreateCommentParams:
    task_id: str
    account_id: str
    content: str
    author_name: str


@dataclass
class GetCommentParams:
    comment_id: str
    task_id: str
    account_id: str


@dataclass
class GetPaginatedCommentsParams:
    task_id: str
    account_id: str
    pagination_params: PaginationParams
    sort_params: Optional[SortParams] = None


@dataclass
class UpdateCommentParams:
    comment_id: str
    task_id: str
    account_id: str
    content: str


@dataclass
class DeleteCommentParams:
    comment_id: str
    task_id: str
    account_id: str


@dataclass
class CommentDeletionResult:
    comment_id: str
    deleted_at: datetime
    success: bool


@dataclass(frozen=True)
class CommentErrorCode:
    NOT_FOUND: str = "COMMENT_ERR_01"
    BAD_REQUEST: str = "COMMENT_ERR_02"
    ACCESS_DENIED: str = "COMMENT_ERR_03"
