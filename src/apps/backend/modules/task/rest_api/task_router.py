from flask import Blueprint

from modules.task.rest_api.task_view import TaskView,TaskCommentView


class TaskRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks", view_func=TaskView.as_view("task_view"), methods=["POST", "GET"]
        )
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>",
            view_func=TaskView.as_view("task_view_by_id"),
            methods=["GET", "PATCH", "DELETE"],
        )

        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments",
            view_func=TaskCommentView.as_view("add_comment"),
            methods=["POST"]
        )

        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>/comments/<comment_id>",
            view_func=TaskCommentView.as_view("delete_comment"),
            methods=["DELETE"]
        )

        return blueprint
