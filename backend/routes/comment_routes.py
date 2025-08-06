from flask import Blueprint, request, jsonify
from services.comment_service import create_comment, get_all_comments, update_comment, delete_comment

comment_bp = Blueprint('comments', __name__, url_prefix='/comments')

@comment_bp.route('/', methods=['GET'])
def get_comments():
    comments = get_all_comments()
    return jsonify([{"id": c.id, "task_id": c.task_id, "content": c.content} for c in comments])

@comment_bp.route('/', methods=['POST'])
def add_comment():
    data = request.get_json()
    comment = create_comment(data['task_id'], data['content'])
    return jsonify({"id": comment.id, "task_id": comment.task_id, "content": comment.content})

@comment_bp.route('/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    data = request.get_json()
    comment = update_comment(comment_id, data['content'])
    if comment:
        return jsonify({"id": comment.id, "task_id": comment.task_id, "content": comment.content})
    else:
        return jsonify({"error": "Comment not found"}), 404

@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
def remove_comment(comment_id):
    comment = delete_comment(comment_id)
    if comment:
        return jsonify({"message": "Comment deleted"})
    else:
        return jsonify({"error": "Comment not found"}), 404
