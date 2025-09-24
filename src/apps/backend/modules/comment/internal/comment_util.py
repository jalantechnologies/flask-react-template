from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.types import Comment


class CommentUtil:
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict) -> Comment:
        return Comment(
            id=str(comment_bson["_id"]),
            task_id=comment_bson["task_id"],
            account_id=comment_bson["account_id"],
            content=comment_bson["content"],
        )
