from flask import Blueprint

from modules.comment.rest_api.comment_view import CommentView


class CommentRouter:
    @staticmethod
    def create_route(blueprint: Blueprint) -> Blueprint:
        # Fix: Add account_id in the route
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments",
            view_func=CommentView.as_view("task_comments"),
            methods=["GET", "POST"],
        )

        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments/<comment_id>",
            view_func=CommentView.as_view("task_comment_by_id"),
            methods=["GET", "PATCH", "DELETE"],
        )

        return blueprint
