from flask import Blueprint, request, jsonify
from app import db
from models.comment import Comment

comment_bp = Blueprint('comment', __name__, url_prefix='/api/comments')

# CREATE
@comment_bp.route('', methods=['POST'])
def create_comment():
    data = request.get_json()
    new_comment = Comment(task_id=data['task_id'], content=data['content'])
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'id': new_comment.id}), 201

# READ (Get all comments for a task)
@comment_bp.route('/task/<int:task_id>', methods=['GET'])
def get_comments(task_id):
    comments = Comment.query.filter_by(task_id=task_id).all()
    return jsonify([{'id': c.id, 'content': c.content} for c in comments])

# UPDATE
@comment_bp.route('/<int:id>', methods=['PUT'])
def update_comment(id):
    data = request.get_json()
    comment = Comment.query.get_or_404(id)
    comment.content = data['content']
    db.session.commit()
    return jsonify({'message': 'Comment updated'})

# DELETE
@comment_bp.route('/<int:id>', methods=['DELETE'])
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted'})
