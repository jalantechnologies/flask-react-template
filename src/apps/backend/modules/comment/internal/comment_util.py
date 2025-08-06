from modules.comment.types import Comment


class CommentUtil:
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict) -> Comment:
        return Comment(
            id=str(comment_bson["_id"]),
            account_id=comment_bson["account_id"],
            task_id=comment_bson["task_id"],
            content=comment_bson["content"],
            created_at=comment_bson["created_at"],
            updated_at=comment_bson["updated_at"],
        )