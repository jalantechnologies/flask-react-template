from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from apps.backend.modules.database import get_db  # Adjust if using a different method
from apps.backend.modules.models.comment import Comment

bp = Blueprint("comments", __name__)

@bp.route("/tasks/<int:task_id>/comments/", methods=["POST"])
def create_comment(task_id):
    db: Session = get_db()
    data = request.get_json()
    content = data.get("content")
    if not content:
        return jsonify({"error": "Content is required"}), 400

    comment = Comment(task_id=task_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return jsonify({"id": comment.id, "content": comment.content}), 201


@bp.route("/tasks/<int:task_id>/comments/", methods=["GET"])
def get_comments(task_id):
    db: Session = get_db()
    comments = db.query(Comment).filter(Comment.task_id == task_id).all()
    return jsonify([{"id": c.id, "content": c.content} for c in comments])


@bp.route("/comments/<int:comment_id>/", methods=["PUT"])
def update_comment(comment_id):
    db: Session = get_db()
    data = request.get_json()
    comment = db.query(Comment).get(comment_id)

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    comment.content = data.get("content", comment.content)
    db.commit()
    db.refresh(comment)

    return jsonify({"id": comment.id, "content": comment.content})


@bp.route("/comments/<int:comment_id>/", methods=["DELETE"])
def delete_comment(comment_id):
    db: Session = get_db()
    comment = db.query(Comment).get(comment_id)

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    db.delete(comment)
    db.commit()
    return jsonify({"message": "Comment deleted"})
