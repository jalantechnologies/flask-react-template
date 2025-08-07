from typing import Any

from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.types import Comment


class CommentUtil:
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict[str, Any]) -> Comment:
        validated_comment_data = CommentModel.from_bson(comment_bson)
        return Comment(
            id=str(validated_comment_data.id),
            task_id=validated_comment_data.task_id,
            account_id=validated_comment_data.account_id,
            content=validated_comment_data.content,
            created_at=validated_comment_data.created_at,
            updated_at=validated_comment_data.updated_at,
        )
