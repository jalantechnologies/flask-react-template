from flask import Blueprint

from modules.task_comment.rest_api.task_comment_router import TaskCommentRouter


class TaskCommentRestApiServer:
    """Factory for creating task comment REST API blueprint"""
    
    @staticmethod
    def create() -> Blueprint:
        """Create and configure the task comment API blueprint"""
        task_comment_api_blueprint = Blueprint("task_comment", __name__)
        return TaskCommentRouter.create_route(blueprint=task_comment_api_blueprint)