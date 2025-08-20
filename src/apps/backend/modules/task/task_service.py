from modules.application.common.types import PaginationResult
from modules.task.internal.task_reader import TaskReader
from modules.task.internal.task_writer import TaskWriter
from modules.task.comment_service import CommentService
from modules.task.types import (
    CreateTaskParams,
    DeleteTaskParams,
    GetPaginatedTasksParams,
    GetTaskParams,
    Task,
    TaskDeletionResult,
    UpdateTaskParams,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetCommentsForTaskParams,
    Comment,
    CommentDeletionResult,
    UpdateCommentParams,
)


class TaskService:
    @staticmethod
    def create_task(*, params: CreateTaskParams) -> Task:
        return TaskWriter.create_task(params=params)

    @staticmethod
    def get_task(*, params: GetTaskParams) -> Task:
        return TaskReader.get_task(params=params)

    @staticmethod
    def get_paginated_tasks(*, params: GetPaginatedTasksParams) -> PaginationResult[Task]:
        return TaskReader.get_paginated_tasks(params=params)

    @staticmethod
    def update_task(*, params: UpdateTaskParams) -> Task:
        return TaskWriter.update_task(params=params)

    @staticmethod
    def delete_task(*, params: DeleteTaskParams) -> TaskDeletionResult:
        return TaskWriter.delete_task(params=params)

    # Comment operations
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        return CommentService.create_comment(params=params)

    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        return CommentService.get_comment(params=params)

    @staticmethod
    def get_comments_for_task(*, params: GetCommentsForTaskParams) -> PaginationResult[Comment]:
        return CommentService.get_comments_for_task(params=params)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        return CommentService.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        return CommentService.delete_comment(params=params)
