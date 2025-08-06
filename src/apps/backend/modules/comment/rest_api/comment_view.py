from flask import request, jsonify
from comment.comment_service import (
    create_comment,
    update_comment,
    delete_comment,
    get_comments_by_task
)

def add_comment():
    data = request.json
    c = create_comment(data["content"], data["task_id"])
    return jsonify({"id": c.id}), 201

def update_comment_view(comment_id):
    data = request.json
    c = update_comment(comment_id, data["content"])
    return jsonify({"id": c.id}), 200

def delete_comment_view(comment_id):
    delete_comment(comment_id)
    return jsonify({"status": "deleted"}), 200

def list_comments(task_id):
    comments = get_comments_by_task(task_id)
    return jsonify([c.to_dict() for c in comments])
