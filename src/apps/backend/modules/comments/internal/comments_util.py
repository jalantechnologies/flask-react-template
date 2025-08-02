from modules.comments.types import Comment

from .store.comments_model import CommentModel


def convert_comment_bson_to_comment(bson: dict) -> Comment:
    model = CommentModel.from_bson(bson)
    return Comment(
        id=str(model.id),
        task_id=model.task_id,
        account_id=model.account_id,
        content=model.content,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
