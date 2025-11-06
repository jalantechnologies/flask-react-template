from flask.views import MethodView
from flask import request, jsonify
from modules.authentication.rest_api.decorators.login_required import login_required


class CommentView(MethodView):
    def __init__(self, service):
        self.service = service

    @login_required
    def get(self, account_id, task_id, comment_id=None):
        """Get all comments for a task OR a specific comment by ID"""

        try:
            if comment_id:
                comment = self.service.get(account_id, task_id, comment_id)
                if not comment:
                    return jsonify({"message": "Comment not found"}), 404

                return jsonify(comment.to_dict()), 200

            comments = self.service.list_for_task(account_id, task_id)
            return jsonify([c.to_dict() for c in comments]), 200

        except ValueError as e:
            return jsonify({"message": str(e)}), 404

    @login_required
    def post(self, account_id, task_id):
        """Create a new comment for a task"""
        data = request.get_json(silent=True) or {}
        body = (data.get("body") or "").strip()

        if not body:
            return jsonify({"message": "body is required"}), 400

        # Username injected from login_required decorator
        author = request.account.username

        try:
            comment = self.service.create(account_id, task_id, body, author)
            return jsonify(comment.to_dict()), 201

        except ValueError as e:
            return jsonify({"message": str(e)}), 404

    @login_required
    def patch(self, account_id, task_id, comment_id):
        """Update an existing comment"""
        data = request.get_json(silent=True) or {}
        new_body = data.get("body")

        try:
            updated_comment = self.service.update(account_id, task_id, comment_id, body=new_body)
            if not updated_comment:
                return jsonify({"message": "Comment not found"}), 404

            return jsonify(updated_comment.to_dict()), 200

        except ValueError as e:
            return jsonify({"message": str(e)}), 404

    @login_required
    def delete(self, account_id, task_id, comment_id):
        """Delete a comment"""
        try:
            deleted = self.service.delete(account_id, task_id, comment_id)
            if not deleted:
                return jsonify({"message": "Comment not found"}), 404

            return jsonify({"message": "Comment deleted successfully"}), 200

        except ValueError as e:
            return jsonify({"message": str(e)}), 404