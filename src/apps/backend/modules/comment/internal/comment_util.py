from typing import Any

from bson.objectid import ObjectId

from modules.comment.errors import CommentTaskNotFoundError
from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.types import Comment
from modules.task.internal.store.task_repository import TaskRepository


class CommentUtil:
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict[str, Any]) -> Comment:
        validated_comment_data = CommentModel.from_bson(comment_bson)
        return Comment(
            account_id=validated_comment_data.account_id,
            content=validated_comment_data.content,
            id=str(validated_comment_data.id),
            task_id=validated_comment_data.task_id,
        )

    @staticmethod
    def validate_task_exists(account_id: str, task_id: str) -> None:
        task_bson = TaskRepository.collection().find_one(
            {"_id": ObjectId(task_id), "account_id": account_id, "active": True}
        )
        if task_bson is None:
            raise CommentTaskNotFoundError(task_id=task_id)

        return
