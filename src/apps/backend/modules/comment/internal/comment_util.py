from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.types import Comment


class CommentUtil:
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict) -> Comment:
        comment_model = CommentModel.from_bson(comment_bson)
        return Comment(
            id=str(comment_model.id),
            task_id=comment_model.task_id,
            account_id=comment_model.account_id,
            content=comment_model.content,
            author_name=comment_model.author_name,
            active=comment_model.active,
            created_at=comment_model.created_at,
            updated_at=comment_model.updated_at,
        )
