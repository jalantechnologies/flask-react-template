from flask import request, jsonify
from flask.views import MethodView

from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.internal.store.comment_repository import CommentRepository


class CommentView(MethodView):
    """Handle comment operations for a specific task"""
    
    def post(self, account_id: str, task_id: str):
        """Create a new comment"""
        data = request.get_json()
        
        if not data or "content" not in data:
            return jsonify({"error": "Content is required"}), 400
        
        comment = CommentModel(
            task_id=task_id,
            account_id=account_id,
            content=data["content"]
        )
        
        created_comment = CommentRepository.create(comment)
        
        return jsonify({
            "id": str(created_comment.id),
            "task_id": created_comment.task_id,
            "content": created_comment.content,
            "created_at": created_comment.created_at.isoformat(),
            "updated_at": created_comment.updated_at.isoformat()
        }), 201
    
    def get(self, account_id: str, task_id: str):
        """Get all comments for a task"""
        comments = CommentRepository.find_by_task_id(task_id, account_id)
        
        return jsonify({
            "comments": [
                {
                    "id": str(comment.id),
                    "task_id": comment.task_id,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                    "updated_at": comment.updated_at.isoformat()
                }
                for comment in comments
            ]
        }), 200


class CommentViewById(MethodView):
    """Handle operations on a specific comment"""
    
    def get(self, account_id: str, task_id: str, comment_id: str):
        """Get a specific comment"""
        comment = CommentRepository.find_by_id(comment_id, account_id)
        
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        
        return jsonify({
            "id": str(comment.id),
            "task_id": comment.task_id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat()
        }), 200
    
    def patch(self, account_id: str, task_id: str, comment_id: str):
        """Update a comment"""
        data = request.get_json()
        
        if not data or "content" not in data:
            return jsonify({"error": "Content is required"}), 400
        
        updated_comment = CommentRepository.update(comment_id, account_id, data["content"])
        
        if not updated_comment:
            return jsonify({"error": "Comment not found or not authorized"}), 404
        
        return jsonify({
            "id": str(updated_comment.id),
            "task_id": updated_comment.task_id,
            "content": updated_comment.content,
            "created_at": updated_comment.created_at.isoformat(),
            "updated_at": updated_comment.updated_at.isoformat()
        }), 200
    
    def delete(self, account_id: str, task_id: str, comment_id: str):
        """Delete a comment"""
        success = CommentRepository.delete(comment_id, account_id)
        
        if not success:
            return jsonify({"error": "Comment not found or not authorized"}), 404
        
        return jsonify({"message": "Comment deleted successfully"}), 200