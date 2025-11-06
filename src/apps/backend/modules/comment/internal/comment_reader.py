from typing import Optional, List
from .store.comment_model import CommentModel
from .store.comment_repository import CommentRepository


class CommentReader:
    """
    Reader class to fetch comments from MongoDB.
    Only reads data — no write/update/delete operations here.
    """

    def __init__(self, repository: CommentRepository) -> None:
        self.repository = repository

    def get(self, comment_id: str) -> Optional[CommentModel]:
        """Fetch a single comment by ID."""
        return self.repository.find_by_id(comment_id)

    def list_for_task(self, task_id: str) -> List[CommentModel]:
        """Fetch all comments for a given task."""
        return self.repository.list_for_task(task_id)
