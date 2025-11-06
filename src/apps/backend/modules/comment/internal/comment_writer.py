from typing import Optional
from .store.comment_model import CommentModel
from .store.comment_repository import CommentRepository


class CommentWriter:
    """
    Writer class for creating, updating, and deleting comments.
    Only writes data — no read-only operations here.
    """

    def __init__(self, repository: CommentRepository) -> None:
        self.repository = repository

    def create(self, task_id: str, body: str, author: Optional[str]) -> CommentModel:
        model = CommentModel(task_id=task_id, body=body, author=author)
        return self.repository.create(model)

    def update(self, comment_id: str, *, body=None, author=None) -> Optional[CommentModel]:
        fields = {}

        if body is not None:
            fields["body"] = body
        if author is not None:
            fields["author"] = author

        return self.repository.update(comment_id, fields)

    def delete(self, comment_id: str) -> bool:
        return self.repository.delete(comment_id)