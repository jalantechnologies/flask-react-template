from flask import Blueprint

from modules.comment.rest_api.comment_view import CommentByIdView, CommentView


class CommentRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule(
            "/tasks/<task_id>/comments", view_func=CommentView.as_view("comment_view"), methods=["POST", "GET"]
        )
        blueprint.add_url_rule(
            "/comments/<comment_id>", view_func=CommentByIdView.as_view("comment_by_id_view"), methods=["PUT", "DELETE"]
        )

        return blueprint
