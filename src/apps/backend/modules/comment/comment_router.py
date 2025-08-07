from flask import Blueprint, request, jsonify
from src.apps.backend.modules.comment import comment_repository as repo

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/comments', methods=['POST'])
def create_comment():
    data = request.json
    comment = repo.create_comment(data['task_id'], data['content'])
    return jsonify(comment.to_dict()), 201

@comment_bp.route('/comments', methods=['GET'])
def get_all_comments():
    comments = repo.get_all_comments()
    return jsonify([c.to_dict() for c in comments])

@comment_bp.route('/comments/<int:id>', methods=['PUT'])
def update_comment(id):
    data = request.json
    comment = repo.update_comment(id, data['content'])
    return jsonify(comment.to_dict()), 200

@comment_bp.route('/comments/<int:id>', methods=['DELETE'])
def delete_comment(id):
    repo.delete_comment(id)
    return jsonify({'message': 'Comment deleted'})
