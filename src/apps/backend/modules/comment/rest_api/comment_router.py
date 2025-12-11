from flask import Blueprint
from modules.comment.rest_api.comment_view import CommentView


class CommentRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        # Route for creating and listing comments for a specific task
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments",
            view_func=CommentView.as_view("comment_view"),
            methods=["POST", "GET"]
        )
        
        # Route for getting, updating, and deleting a specific comment
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments/<comment_id>",
            view_func=CommentView.as_view("comment_view_by_id"),
            methods=["GET", "PATCH", "DELETE"],
        )
        
        return blueprint