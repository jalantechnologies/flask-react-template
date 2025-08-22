from flask import Blueprint

from modules.task_comment.rest_api.task_comment_view import TaskCommentView, TaskCommentDetailView


class TaskCommentRouter:
    """Router for task comment endpoints"""
    
    @staticmethod
    def create_route(*, blueprint: Blueprint) -> Blueprint:
        """
        Register task comment routes
        
        Routes:
        - GET/POST /api/tasks/{task_id}/comments
        - GET/PUT/DELETE /api/tasks/{task_id}/comments/{comment_id}
        """
        
        # Comments collection endpoints
        blueprint.add_url_rule(
            "/tasks/<string:task_id>/comments",
            view_func=TaskCommentView.as_view("task_comments_view"),
            methods=["GET", "POST"]
        )
        
        # Individual comment endpoints
        blueprint.add_url_rule(
            "/tasks/<string:task_id>/comments/<string:comment_id>",
            view_func=TaskCommentDetailView.as_view("task_comment_detail_view"),
            methods=["GET", "PUT", "DELETE"]
        )
        
        return blueprint