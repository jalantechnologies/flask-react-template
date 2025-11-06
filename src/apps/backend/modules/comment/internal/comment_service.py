from typing import Optional
from modules.task.internal.task_reader import TaskReader
from modules.task.types import GetTaskParams
from .comment_reader import CommentReader
from .comment_writer import CommentWriter


class CommentService:
    """
    Handles business logic for Comments with account-level task validation.
    Ensures comments can only be added, updated, or viewed by the task owner.
    """

    def __init__(self, task_reader: TaskReader, reader: CommentReader, writer: CommentWriter) -> None:
        self.task_reader = task_reader
        self.reader = reader
        self.writer = writer

    def _ensure_task(self, account_id: str, task_id: str):
        """
        Verify the task exists and belongs to the given account.
        Uses TaskReader.get_task() with GetTaskParams.
        """
        params = GetTaskParams(account_id=account_id, task_id=task_id)

        try:
            self.task_reader.get_task(params=params)
        except Exception:
            raise ValueError(f"Task with id '{task_id}' not found for this account")

    def create(self, account_id: str, task_id: str, body: str, author: Optional[str]):
        """
        Create a new comment for a task.
        """
        self._ensure_task(account_id, task_id)

        if not body or not body.strip():
            raise ValueError("`body` is required")

        return self.writer.create(task_id=task_id, body=body, author=author)

    def list_for_task(self, account_id: str, task_id: str):
        """
        Get all comments belonging to a task.
        """
        self._ensure_task(account_id, task_id)
        return self.reader.list_for_task(task_id)

    def get(self, account_id: str, task_id: str, comment_id: str):
        """
        Get a specific comment by ID.
        """
        self._ensure_task(account_id, task_id)
        return self.reader.get(comment_id)

    def update(self, account_id: str, task_id: str, comment_id: str, *, body=None, author=None):
        """
        Update a comment's content (and optionally author in future).
        """
        self._ensure_task(account_id, task_id)

        if body is not None and not body.strip():
            raise ValueError("`body` cannot be empty")

        return self.writer.update(comment_id, body=body, author=author)

    def delete(self, account_id: str, task_id: str, comment_id: str) -> bool:
        """
        Delete a specific comment.
        """
        self._ensure_task(account_id, task_id)
        return self.writer.delete(comment_id)