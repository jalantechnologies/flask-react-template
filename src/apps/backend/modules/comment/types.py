from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modules.application.common.types import PaginationParams


@dataclass
class Comment:
    id: str
    account_id: str
    task_id: str
    content: str
    active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class CreateCommentParams:
    account_id: str
    task_id: str
    content: str


@dataclass
class GetCommentParams:
    account_id: str
    task_id: str
    comment_id: str


@dataclass
class GetPaginatedCommentsParams:
    account_id: str
    task_id: str
    pagination_params: PaginationParams
    sort_params: Optional[dict] = None


@dataclass
class UpdateCommentParams:
    account_id: str
    task_id: str
    comment_id: str
    content: str


@dataclass
class DeleteCommentParams:
    account_id: str
    task_id: str
    comment_id: str


@dataclass
class CommentDeletionResult:
    comment_id: str
    deleted: bool


@dataclass(frozen=True)
class CommentErrorCode:
    NOT_FOUND: str = "COMMENT_ERR_01"
    BAD_REQUEST: str = "COMMENT_ERR_02"
