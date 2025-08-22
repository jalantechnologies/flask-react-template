from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView
from pydantic import ValidationError

from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware
from modules.task_comment.task_comment_service import TaskCommentService
from modules.task_comment.types import (
    CreateTaskCommentParams,
    UpdateTaskCommentParams,
    DeleteTaskCommentParams,
    GetTaskCommentsParams,
    CreateTaskCommentRequest,
    UpdateTaskCommentRequest,
    TaskCommentFilters
)
from modules.application.common.types import PaginationParams
from modules.logger.logger import Logger


class TaskCommentView(MethodView):
    """
    Handles task comment collection operations
    GET /api/tasks/{task_id}/comments - Get all comments for a task
    POST /api/tasks/{task_id}/comments - Create a new comment
    """
    #Protect all the routes with auth middleware
    decorators = [access_auth_middleware]  # Require authentication
    
    def get(self, task_id: str) -> ResponseReturnValue:
        """Get all comments for a task with optional filtering and pagination"""
        try:
            # Parse query parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)
            
            # Optional filters
            author_id = request.args.get('author_id')
            created_after = request.args.get('created_after')
            created_before = request.args.get('created_before')
            
            # Build filters if any provided
            filters = None
            if any([author_id, created_after, created_before]):
                filter_dict = {}
                if author_id:
                    filter_dict['author_id'] = author_id
                if created_after:
                    filter_dict['created_after'] = created_after
                if created_before:
                    filter_dict['created_before'] = created_before
                    
                filters = TaskCommentFilters(**filter_dict)
            
            # Build params
            params = GetTaskCommentsParams(
                task_id=task_id,
                account_id=request.account_id,  # From auth middleware
                pagination_params=PaginationParams(page=page, size=limit)
            )
            
            # Get comments
            response = TaskCommentService.get_task_comments(params, filters)
            
            return jsonify(response.model_dump()), 200
            
        except ValidationError as e:
            return jsonify({
                "message": "Invalid request parameters",
                "errors": e.errors()
            }), 400
        except Exception as e:
            Logger.error(message=f"Error retrieving comments: {str(e)}")
            return jsonify({
                "message": "Failed to retrieve comments",
                "error": str(e)
            }), 500
    
    def post(self, task_id: str) -> ResponseReturnValue:
        """Create a new comment on a task"""
        try:
            # Parse request body
            request_data = request.get_json()
            if not request_data:
                return jsonify({"message": "Request body is required"}), 400
            
            # Validate request
            comment_request = CreateTaskCommentRequest(**request_data)
            
            # Build params
            params = CreateTaskCommentParams(
                task_id=task_id,
                account_id=request.account_id,  # From auth middleware
                content=comment_request.content
            )
            
            # Create comment
            comment = TaskCommentService.create_comment(params)
            
            return jsonify(comment.model_dump()), 201
            
        except ValidationError as e:
            return jsonify({
                "message": "Invalid request data",
                "errors": e.errors()
            }), 400
        except Exception as e:
            Logger.error(message=f"Error creating comment: {str(e)}")
            # Return proper error response based on exception type
            if hasattr(e, 'http_status_code'):
                return jsonify({"message": e.message}), e.http_status_code
            return jsonify({
                "message": "Failed to create comment",
                "error": str(e)
            }), 500


class TaskCommentDetailView(MethodView):
    """
    Handles individual task comment operations
    PUT /api/tasks/{task_id}/comments/{comment_id} - Update a comment
    DELETE /api/tasks/{task_id}/comments/{comment_id} - Delete a comment
    GET /api/tasks/{task_id}/comments/{comment_id} - Get a single comment
    """
    #Protect all the routes with auth middleware
    decorators = [access_auth_middleware]
    
    def get(self, task_id: str, comment_id: str) -> ResponseReturnValue:
        """Get a single comment by ID"""
        try:
            comment = TaskCommentService.get_comment_by_id(comment_id)
            
            if not comment:
                return jsonify({"message": f"Comment {comment_id} not found"}), 404
            
            # Verify the comment belongs to the specified task
            if comment.task_id != task_id:
                return jsonify({"message": "Comment does not belong to this task"}), 404
            
            return jsonify(comment.model_dump()), 200
            
        except Exception as e:
            Logger.error(message=f"Error retrieving comment: {str(e)}")
            return jsonify({
                "message": "Failed to retrieve comment",
                "error": str(e)
            }), 500
    
    def put(self, task_id: str, comment_id: str) -> ResponseReturnValue:
        """Update an existing comment"""
        try:
            # Parse request body
            request_data = request.get_json()
            if not request_data:
                return jsonify({"message": "Request body is required"}), 400
            
            # Validate request
            update_request = UpdateTaskCommentRequest(**request_data)
            
            # Build params
            params = UpdateTaskCommentParams(
                comment_id=comment_id,
                task_id=task_id,
                account_id=request.account_id,  # From auth middleware
                content=update_request.content
            )
            
            # Update comment
            comment = TaskCommentService.update_comment(params)
            
            return jsonify(comment.model_dump()), 200
            
        except ValidationError as e:
            return jsonify({
                "message": "Invalid request data",
                "errors": e.errors()
            }), 400
        except Exception as e:
            Logger.error(message=f"Error updating comment: {str(e)}")
            # Return proper error response based on exception type
            if hasattr(e, 'http_status_code'):
                return jsonify({"message": e.message}), e.http_status_code
            return jsonify({
                "message": "Failed to update comment",
                "error": str(e)
            }), 500
    
    def delete(self, task_id: str, comment_id: str) -> ResponseReturnValue:
        """Delete a comment"""
        try:
            # Build params
            params = DeleteTaskCommentParams(
                comment_id=comment_id,
                task_id=task_id,
                account_id=request.account_id  # From auth middleware
            )
            
            # Delete comment
            result = TaskCommentService.delete_comment(params)
            
            return jsonify(result.model_dump()), 200
            
        except Exception as e:
            Logger.error(message=f"Error deleting comment: {str(e)}")
            # Return proper error response based on exception type
            if hasattr(e, 'http_status_code'):
                return jsonify({"message": e.message}), e.http_status_code
            return jsonify({
                "message": "Failed to delete comment",
                "error": str(e)
            }), 500