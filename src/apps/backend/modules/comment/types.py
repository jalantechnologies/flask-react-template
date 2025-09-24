from dataclasses import dataclass
from typing import Optional

from modules.application.common.types import PaginationParams, PaginationResult, SortParams


@dataclass(frozen=True)
class Comment:
    id: str
    task_id: str
    account_id: str
    content: str


@dataclass(frozen=True)
class GetCommentParams:
    task_id: str
    account_id: str
    comment_id: str


@dataclass(frozen=True)
class GetPaginatedCommentsParams:
    task_id: str
    account_id: str
    pagination_params: PaginationParams
    sort_params: Optional[SortParams] = None


@dataclass(frozen=True)
class CreateCommentParams:
    task_id: str
    account_id: str
    content: str


@dataclass(frozen=True)
class UpdateCommentParams:
    task_id: str
    account_id: str
    comment_id: str
    content: str


@dataclass(frozen=True)
class DeleteCommentParams:
    task_id: str
    account_id: str
    comment_id: str


@dataclass(frozen=True)
class CommentDeletionResult:
    success: bool
