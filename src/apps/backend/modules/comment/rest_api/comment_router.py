from flask import Blueprint

from modules.comment.rest_api.comment_view import CommentDetailView, CommentListView


class CommentRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments",
            view_func=CommentListView.as_view("comment_list_view"),
            methods=["POST", "GET"],
        )
        blueprint.add_url_rule(
            "/accounts/<account_id>/comments/<comment_id>",
            view_func=CommentDetailView.as_view("comment_detail_view"),
            methods=["PATCH", "DELETE"],
        )

        return blueprint
