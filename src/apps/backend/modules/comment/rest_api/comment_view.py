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
    GetCommentsParams,
    UpdateCommentParams,
)


class CommentListView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        create_params = CreateCommentParams(
            account_id=account_id, task_id=task_id, content=request_data["content"]
        )

        created_comment = CommentService.create_comment(params=create_params)
        return jsonify(asdict(created_comment)), 201

    @access_auth_middleware
    def get(self, account_id: str, task_id: str) -> ResponseReturnValue:
        get_params = GetCommentsParams(account_id=account_id, task_id=task_id)
        comments = CommentService.get_comments_by_task(params=get_params)
        return jsonify([asdict(comment) for comment in comments]), 200


class CommentDetailView(MethodView):
    @access_auth_middleware
    def patch(self, account_id: str, comment_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise CommentBadRequestError("Request body is required")

        if not request_data.get("content"):
            raise CommentBadRequestError("Content is required")

        update_params = UpdateCommentParams(
            account_id=account_id, comment_id=comment_id, content=request_data["content"]
        )

        updated_comment = CommentService.update_comment(params=update_params)
        return jsonify(asdict(updated_comment)), 200

    @access_auth_middleware
    def delete(self, account_id: str, comment_id: str) -> ResponseReturnValue:
        delete_params = DeleteCommentParams(account_id=account_id, comment_id=comment_id)
        CommentService.delete_comment(params=delete_params)
        return "", 204
