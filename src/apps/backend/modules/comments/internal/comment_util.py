from typing import Any

from modules.comments.internal.store.comment_model import CommentModel
from modules.comments.types import Comment


class CommentUtil:
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict[str, Any]) -> Comment:
        validated_comment_data = CommentModel.from_bson(comment_bson)
        return Comment(
            id=str(validated_comment_data.id),
            account_id=validated_comment_data.account_id,
            task_id=validated_comment_data.task_id,
            content=validated_comment_data.content,
        )
