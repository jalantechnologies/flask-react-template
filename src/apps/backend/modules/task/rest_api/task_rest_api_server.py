from flask import Blueprint

from modules.task.rest_api.task_router import TaskRouter
from modules.task.rest_api.task_comment_router import TaskCommentRouter


class TaskRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        task_api_blueprint = Blueprint("task", __name__)
        TaskRouter.create_route(blueprint=task_api_blueprint)
        TaskCommentRouter.create_route(blueprint=task_api_blueprint)
        return task_api_blueprint
