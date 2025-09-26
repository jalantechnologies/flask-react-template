from flask import Blueprint

from modules.comment.rest_api.comment_view import CommentView


class CommentRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        # Route for creating comments and getting all comments for a task
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments",
            view_func=CommentView.as_view("task_comments"),
            methods=["GET", "POST"]
        )

        # Route for getting, updating, and deleting a specific comment
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments/<comment_id>",
            view_func=CommentView.as_view("task_comment_by_id"),
            methods=["GET", "PATCH", "DELETE"]
        )

        return blueprint
