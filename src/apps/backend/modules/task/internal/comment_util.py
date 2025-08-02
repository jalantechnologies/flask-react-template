from bson.errors import InvalidId
from bson.objectid import ObjectId

from modules.task.errors import CommentValidationError
from modules.task.internal.store.comment_repository import CommentRepository
from modules.task.internal.store.task_repository import TaskRepository
from modules.task.types import Comment


class CommentUtil:
    @staticmethod
    def validate_comment_content(content: str) -> None:
        if not content or not content.strip():
            raise CommentValidationError("Comment content cannot be empty")

        if len(content.strip()) > 1000:
            raise CommentValidationError("Comment content cannot exceed 1000 characters")

    @staticmethod
    def validate_comment_exists(comment_id: str, task_id: str, account_id: str) -> None:
        try:
            object_id = ObjectId(comment_id)
        except InvalidId:
            raise CommentValidationError("Comment not found")

        comment_bson = CommentRepository.collection().find_one(
            {"_id": object_id, "task_id": task_id, "account_id": account_id, "active": True}
        )
        if not comment_bson:
            raise CommentValidationError("Comment not found")

    @staticmethod
    def validate_task_exists(task_id: str, account_id: str) -> None:
        try:
            object_id = ObjectId(task_id)
        except InvalidId:
            raise CommentValidationError("Task not found")

        task_bson = TaskRepository.collection().find_one({"_id": object_id, "account_id": account_id, "active": True})
        if not task_bson:
            raise CommentValidationError("Task not found")

    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict) -> Comment:
        return Comment(
            id=str(comment_bson["_id"]),
            task_id=comment_bson["task_id"],
            account_id=comment_bson["account_id"],
            content=comment_bson["content"],
            created_at=comment_bson["created_at"],
            updated_at=comment_bson["updated_at"],
        )
