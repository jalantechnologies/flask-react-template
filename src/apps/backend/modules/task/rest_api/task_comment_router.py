from flask import Blueprint

from modules.task.rest_api.task_comment_view import TaskCommentView


class TaskCommentRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule(
            "/accounts/<string:account_id>/tasks/<string:task_id>/comments",
            view_func=TaskCommentView.as_view("task_comments"),
            methods=["POST", "GET"],
        )
        blueprint.add_url_rule(
            "/accounts/<string:account_id>/tasks/<string:task_id>/comments/<string:comment_id>",
            view_func=TaskCommentView.as_view("task_comment_by_id"),
            methods=["GET", "PATCH", "DELETE"],
        )
        return blueprint
