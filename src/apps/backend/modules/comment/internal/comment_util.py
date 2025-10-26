from typing import Any

from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.types import Comment


class CommentUtil:
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict[str, Any]) -> Comment:
        validated_task_data = CommentModel.from_bson(comment_bson)
        return Comment(
            account_id=validated_task_data.account_id,
            text=validated_task_data.text,
            task_id=validated_task_data.task_id,
            id=str(validated_task_data.id),
        )
