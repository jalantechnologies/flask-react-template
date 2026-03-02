from flask import Blueprint

from modules.comment.rest_api.comment_view import CommentView, CommentDetailView


class CommentRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        # Routes for comments on a specific task
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments", 
            view_func=CommentView.as_view("comment_view"), 
            methods=["POST", "GET"]
        )
        
        # Routes for individual comment operations
        blueprint.add_url_rule(
            "/accounts/<account_id>/comments/<comment_id>",
            view_func=CommentDetailView.as_view("comment_detail_view"),
            methods=["PATCH", "DELETE"],
        )

        return blueprint
