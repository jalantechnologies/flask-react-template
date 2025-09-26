from modules.application.common.types import PaginationResult
from modules.comment.errors import CommentTaskNotFoundError
from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_writer import CommentWriter
from modules.comment.types import (
    Comment,
    CommentDeletionResult,
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)
from modules.task.errors import TaskNotFoundError
from modules.task.task_service import TaskService
from modules.task.types import GetTaskParams


class CommentService:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        # Verify that the task exists and belongs to the account
        try:
            TaskService.get_task(params=GetTaskParams(
                account_id=params.account_id,
                task_id=params.task_id
            ))
        except TaskNotFoundError:
            raise CommentTaskNotFoundError(task_id=params.task_id)

        return CommentWriter.create_comment(params=params)

    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        # Verify that the task exists and belongs to the account
        try:
            TaskService.get_task(params=GetTaskParams(
                account_id=params.account_id,
                task_id=params.task_id
            ))
        except TaskNotFoundError:
            raise CommentTaskNotFoundError(task_id=params.task_id)

        return CommentReader.get_comment(params=params)

    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        # Verify that the task exists and belongs to the account
        try:
            TaskService.get_task(params=GetTaskParams(
                account_id=params.account_id,
                task_id=params.task_id
            ))
        except TaskNotFoundError:
            raise CommentTaskNotFoundError(task_id=params.task_id)

        return CommentReader.get_paginated_comments(params=params)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        # Verify that the task exists and belongs to the account
        try:
            TaskService.get_task(params=GetTaskParams(
                account_id=params.account_id,
                task_id=params.task_id
            ))
        except TaskNotFoundError:
            raise CommentTaskNotFoundError(task_id=params.task_id)

        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        # Verify that the task exists and belongs to the account
        try:
            TaskService.get_task(params=GetTaskParams(
                account_id=params.account_id,
                task_id=params.task_id
            ))
        except TaskNotFoundError:
            raise CommentTaskNotFoundError(task_id=params.task_id)

        return CommentWriter.delete_comment(params=params)
