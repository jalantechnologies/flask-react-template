from flask import jsonify, request
from flask.views import MethodView

from modules.application.common.types import PaginationParams, SortParams
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.comment.comment_service import CommentService
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    GetPaginatedCommentsParams,
    UpdateCommentParams,
)


class CommentView(MethodView):
    @access_auth_middleware
    def post(self, account_id: str, task_id: str):
        """Create a new comment for a task"""
        try:
            data = request.get_json()

            if data is None:
                return jsonify({"error": "Request body is required"}), 400

            # Extract and validate required fields
            content = data.get("content")
            author_name = data.get("author_name")

            if not content:
                return jsonify({"error": "Content is required"}), 400

            if not author_name:
                return jsonify({"error": "Author name is required"}), 400

            # Validate field types and constraints
            if not isinstance(content, str) or len(content.strip()) == 0:
                return jsonify({"error": "Content must be a non-empty string"}), 400

            if not isinstance(author_name, str) or len(author_name.strip()) == 0:
                return jsonify({"error": "Author name must be a non-empty string"}), 400

            params = CreateCommentParams(
                task_id=task_id, account_id=account_id, content=content.strip(), author_name=author_name.strip()
            )

            comment = CommentService.create_comment(params=params)
            return (
                jsonify(
                    {
                        "id": comment.id,
                        "task_id": comment.task_id,
                        "account_id": comment.account_id,
                        "content": comment.content,
                        "author_name": comment.author_name,
                        "active": comment.active,
                        "created_at": comment.created_at.isoformat(),
                        "updated_at": comment.updated_at.isoformat(),
                    }
                ),
                201,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @access_auth_middleware
    def get(self, account_id: str, task_id: str, comment_id: str = None):
        """Get a specific comment or list all comments for a task"""
        try:
            if comment_id:
                # Get specific comment
                params = GetCommentParams(comment_id=comment_id, task_id=task_id, account_id=account_id)
                comment = CommentService.get_comment(params=params)
                return (
                    jsonify(
                        {
                            "id": comment.id,
                            "task_id": comment.task_id,
                            "account_id": comment.account_id,
                            "content": comment.content,
                            "author_name": comment.author_name,
                            "active": comment.active,
                            "created_at": comment.created_at.isoformat(),
                            "updated_at": comment.updated_at.isoformat(),
                        }
                    ),
                    200,
                )
            else:
                # Get paginated comments for task
                page = int(request.args.get("page", 1))
                size = int(request.args.get("size", 10))
                sort_by = request.args.get("sort_by")
                sort_order = request.args.get("sort_order", "desc")

                pagination_params = PaginationParams(page=page, size=size)
                sort_params = None
                if sort_by:
                    from modules.application.common.types import SortDirection

                    sort_direction = SortDirection.from_string(sort_order)
                    sort_params = SortParams(sort_by=sort_by, sort_direction=sort_direction)

                params = GetPaginatedCommentsParams(
                    task_id=task_id, account_id=account_id, pagination_params=pagination_params, sort_params=sort_params
                )

                result = CommentService.get_paginated_comments(params=params)
                return (
                    jsonify(
                        {
                            "items": [
                                {
                                    "id": comment.id,
                                    "task_id": comment.task_id,
                                    "account_id": comment.account_id,
                                    "content": comment.content,
                                    "author_name": comment.author_name,
                                    "active": comment.active,
                                    "created_at": comment.created_at.isoformat(),
                                    "updated_at": comment.updated_at.isoformat(),
                                }
                                for comment in result.items
                            ],
                            "pagination": {
                                "page": result.pagination_params.page,
                                "size": result.pagination_params.size,
                                "total_count": result.total_count,
                                "total_pages": result.total_pages,
                            },
                        }
                    ),
                    200,
                )
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @access_auth_middleware
    def patch(self, account_id: str, task_id: str, comment_id: str):
        """Update a comment"""
        try:
            data = request.get_json()

            if data is None:
                return jsonify({"error": "Request body is required"}), 400

            # Extract and validate required fields
            content = data.get("content")

            if not content:
                return jsonify({"error": "Content is required"}), 400

            # Validate field types and constraints
            if not isinstance(content, str) or len(content.strip()) == 0:
                return jsonify({"error": "Content must be a non-empty string"}), 400

            params = UpdateCommentParams(
                comment_id=comment_id, task_id=task_id, account_id=account_id, content=content.strip()
            )

            comment = CommentService.update_comment(params=params)
            return (
                jsonify(
                    {
                        "id": comment.id,
                        "task_id": comment.task_id,
                        "account_id": comment.account_id,
                        "content": comment.content,
                        "author_name": comment.author_name,
                        "active": comment.active,
                        "created_at": comment.created_at.isoformat(),
                        "updated_at": comment.updated_at.isoformat(),
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @access_auth_middleware
    def delete(self, account_id: str, task_id: str, comment_id: str):
        """Delete a comment (soft delete)"""
        try:
            params = DeleteCommentParams(comment_id=comment_id, task_id=task_id, account_id=account_id)

            result = CommentService.delete_comment(params=params)
            return (
                jsonify(
                    {
                        "comment_id": result.comment_id,
                        "deleted_at": result.deleted_at.isoformat(),
                        "success": result.success,
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400
