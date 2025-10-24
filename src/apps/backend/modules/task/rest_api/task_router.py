from flask import Blueprint

from modules.task.rest_api.task_view import TaskView


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

        return blueprint
