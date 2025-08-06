from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.types import Comment


class CommentReader:
    @staticmethod
    def get_comments_by_task_id(task_id: str) -> list[Comment]:
        cursor = CommentRepository.collection().find({"task_id": task_id})
        comments_bson = list(cursor)

        return [
            Comment(
                id=str(comment["_id"]),
                task_id=comment["task_id"],
                account_id=comment["account_id"],
                content=comment["content"],
            )
            for comment in comments_bson
        ]
