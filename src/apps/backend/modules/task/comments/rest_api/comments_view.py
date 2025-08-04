from dataclasses import asdict
from typing import Optional
from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from modules.task.errors import TaskBadRequestError
from modules.application.common.constants import DEFAULT_PAGINATION_PARAMS
from modules.application.common.types import PaginationParams
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.task.comments.comment_service import CommentService
from modules.task.comments.types import (
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
)

class CommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise TaskBadRequestError("Request body is required")
        
        if not request_data.get("content"):
            raise TaskBadRequestError("Content is required")

        params = CreateCommentParams(
            account_id=account_id,
            task_id=task_id,
            content=request_data.get("content")
        )

        comment = CommentService.create_comment(params=params)

        return jsonify(asdict(comment))

    @access_auth_middleware
    def get(self, account_id: str, task_id: str, comment_id: Optional[str] = None) -> ResponseReturnValue:
        if comment_id:
            params = GetCommentParams(
                account_id=account_id,
                task_id=task_id,
                comment_id=comment_id
            )
            comment = CommentService.get_comment(params=params)
            return jsonify(asdict(comment)), 200
        else:
            page = request.args.get("page", type=int)
            size = request.args.get("size", type=int)

            if page is not None and page < 1:
                raise TaskBadRequestError("Page must be greater than 0")
            
            if size is not None and size < 1:
                raise TaskBadRequestError("Size must be greater than 0")
            
            pagination_params = PaginationParams(page=page, size=size, offset = 0)
            comments_params = GetPaginatedCommentsParams(
                account_id=account_id,
                task_id=task_id,
                pagination_params=pagination_params
            )

            pagination_result = CommentService.get_paginated_comments(params=comments_params)
            response_data = asdict(pagination_result)
            return jsonify(response_data), 200
    
    @access_auth_middleware
    def patch(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise TaskBadRequestError("Request body is required")
        
        if not request_data.get("content"):
            raise TaskBadRequestError("Content is required")

        params = UpdateCommentParams(
            account_id=account_id,
            task_id=task_id,
            comment_id=comment_id,
            content=request_data.get("content")
        )

        comment = CommentService.update_comment(params=params)

        return jsonify(asdict(comment)), 200
    
    @access_auth_middleware
    def delete(self, account_id: str, task_id: str, comment_id: str) -> ResponseReturnValue:
        delete_params = DeleteCommentParams(
            account_id=account_id,
            task_id=task_id,
            comment_id=comment_id)

        
        CommentService.delete_comment(params=delete_params)
        return "", 204