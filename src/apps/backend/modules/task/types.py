from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modules.application.common.types import PaginationParams, PaginationResult, SortParams


@dataclass(frozen=True)
class Task:
    id: str
    account_id: str
    description: str
    title: str


@dataclass(frozen=True)
class GetTaskParams:
    account_id: str
    task_id: str


@dataclass(frozen=True)
class GetPaginatedTasksParams:
    account_id: str
    pagination_params: PaginationParams
    sort_params: Optional[SortParams] = None


@dataclass(frozen=True)
class CreateTaskParams:
    account_id: str
    description: str
    title: str


@dataclass(frozen=True)
class UpdateTaskParams:
    account_id: str
    task_id: str
    description: str
    title: str


@dataclass(frozen=True)
class DeleteTaskParams:
    account_id: str
    task_id: str


@dataclass(frozen=True)
class TaskDeletionResult:
    task_id: str
    deleted_at: datetime
    success: bool


@dataclass(frozen=True)
class TaskErrorCode:
    NOT_FOUND: str = "TASK_ERR_01"
    BAD_REQUEST: str = "TASK_ERR_02"
