from flask import Blueprint
from modules.task.internal.task_reader import TaskReader
from modules.comment.internal.store.comment_repository import CommentRepository
from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_writer import CommentWriter
from modules.comment.internal.comment_service import CommentService
from .comment_view import CommentView

class CommentRouter:
    @staticmethod
    def create() -> Blueprint:
        """
        Creates and returns a blueprint that handles all Comment CRUD routes.
        Route Pattern:
        /api/accounts/<account_id>/tasks/<task_id>/comments
        """
        blueprint = Blueprint("comments_api", __name__)

        # Instantiate dependencies (Dependency Injection)
        task_reader = TaskReader()
        repo = CommentRepository()
        reader = CommentReader(repo)
        writer = CommentWriter(repo)
        service = CommentService(task_reader, reader, writer)

        # Create View
        comment_view = CommentView.as_view("comment_view", service=service)

        # Register Routes
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments",
            view_func=comment_view,
            methods=["GET", "POST"]
        )

        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments/<comment_id>",
            view_func=comment_view,
            methods=["GET", "PATCH", "DELETE"]
        )

        return blueprint
