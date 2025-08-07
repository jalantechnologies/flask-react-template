from dataclasses import asdict
from typing import Optional

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comment.comment_service import CommentService
from modules.comment.errors import CommentBadRequestError
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetTaskCommentsParams,
    UpdateCommentParams,
)


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        create_params = CreateCommentParams(task_id=task_id, account_id=account_id, content=request_data["content"])

        comment = CommentService.create_comment(params=create_params)
        return jsonify(asdict(comment)), 201

    @access_auth_middleware
    def get(self, account_id: str, task_id: str, comment_id: Optional[str] = None) -> ResponseReturnValue:
        if comment_id:
            # Get specific comment
            params = GetCommentParams(task_id=task_id, comment_id=comment_id, account_id=account_id)
            comment = CommentService.get_comment(params=params)
            return jsonify(asdict(comment)), 200
        else:
            # Get all comments for task
            params = GetTaskCommentsParams(task_id=task_id, account_id=account_id)
            comments = CommentService.get_task_comments(params=params)
            return jsonify([asdict(comment) for comment in comments]), 200

    @access_auth_middleware
    def patch(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        params = UpdateCommentParams(
            task_id=task_id, comment_id=comment_id, account_id=account_id, content=request_data["content"]
        )

        comment = CommentService.update_comment(params=params)
        return jsonify(asdict(comment)), 200

    @access_auth_middleware
    def delete(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        params = DeleteCommentParams(task_id=task_id, comment_id=comment_id, account_id=account_id)

        CommentService.delete_comment(params=params)
        return "", 204
