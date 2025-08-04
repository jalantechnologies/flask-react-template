from flask import Blueprint
from modules.task.comments.rest_api.comments_router import CommentRouter
from modules.task.rest_api.task_view import TaskView


class TaskRouter:
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        # Task resource routes
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks", view_func=TaskView.as_view("task_view"), methods=["POST", "GET"]
        )
        blueprint.add_url_rule(
            "/accounts/<account_id>/tasks/<task_id>",
            view_func=TaskView.as_view("task_view_by_id"),
            methods=["GET", "PATCH", "DELETE"],
        )

        # Comment resource routes (nested under tasks)
        # INTEGRATION DECISION: Comments are nested resources under tasks
        # - Maintains clear hierarchy: tasks contain comments
        # - URL structure: /accounts/{account_id}/tasks/{task_id}/comments
        # - Inherits task-level authentication and authorization
        CommentRouter.create_route(blueprint=blueprint)

        return blueprint
