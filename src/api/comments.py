# src/api/comments.py
"""
Comments API blueprint

This module provides simple CRUD endpoints for comments tied to tasks.
It expects the Flask app to expose:
    app.config['MONGO_CLIENT'] -> a pymongo (or mongomock) client
    app.config['MONGO_DBNAME'] -> optional, defaults to 'flaskreact'
"""
from datetime import datetime
from bson.objectid import ObjectId

from flask import Blueprint, current_app, jsonify, request

comments_bp = Blueprint("comments", __name__, url_prefix="/api")


def get_database():
    """
    Retrieve the configured MongoDB database from the Flask app.

    The app should set:
        - MONGO_CLIENT : pymongo.MongoClient (or mongomock client for tests)
        - MONGO_DBNAME : name of the db (optional)

    Raises:
        RuntimeError: if MONGO_CLIENT is not configured.
    """
    client = current_app.config.get("MONGO_CLIENT")
    if client is None:
        raise RuntimeError("MongoDB client is not configured on the app.")
    db_name = current_app.config.get("MONGO_DBNAME", "flaskreact")
    return client[db_name]


@comments_bp.route("/tasks/<task_id>/comments", methods=["POST"])
def create_comment(task_id):
    """
    Create a new comment for a specific task.

    Expected JSON body:
        { "content": "<text>", "author": "<name (optional)>" }

    Returns:
        201 + created comment metadata on success,
        400 if 'content' is missing.
    """
    payload = request.get_json(silent=True) or {}
    content = payload.get("content")
    author = payload.get("author", "anonymous")

    if not content:
        return jsonify({"error": "Please provide comment content."}), 400

    db = get_database()
    now = datetime.utcnow()
    comment_doc = {
        "task_id": str(task_id),
        "content": content,
        "author": author,
        "created_at": now,
        "updated_at": now,
    }

    result = db.comments.insert_one(comment_doc)

    return (
        jsonify(
            {
                "id": str(result.inserted_id),
                "task_id": comment_doc["task_id"],
                "content": comment_doc["content"],
                "author": comment_doc["author"],
            }
        ),
        201,
    )


@comments_bp.route("/tasks/<task_id>/comments", methods=["GET"])
def list_comments(task_id):
    """
    Return all comments for a task, newest first (sorted by created_at desc).
    """
    db = get_database()
    cursor = db.comments.find({"task_id": str(task_id)}).sort("created_at", -1)

    comments = []
    for doc in cursor:
        comments.append(
            {
                "id": str(doc.get("_id")),
                "task_id": doc.get("task_id"),
                "content": doc.get("content"),
                "author": doc.get("author"),
                "created_at": doc.get("created_at").isoformat()
                if doc.get("created_at")
                else None,
                "updated_at": doc.get("updated_at").isoformat()
                if doc.get("updated_at")
                else None,
            }
        )

    return jsonify(comments), 200


@comments_bp.route("/comments/<comment_id>", methods=["GET"])
def get_comment(comment_id):
    """
    Fetch a single comment by its ID.
    Returns 400 for invalid id format, 404 if not found.
    """
    db = get_database()
    try:
        obj = db.comments.find_one({"_id": ObjectId(comment_id)})
    except Exception:
        return jsonify({"error": "Comment id is invalid."}), 400

    if not obj:
        return jsonify({"error": "Comment not found."}), 404

    return (
        jsonify(
            {
                "id": str(obj.get("_id")),
                "task_id": obj.get("task_id"),
                "content": obj.get("content"),
                "author": obj.get("author"),
            }
        ),
        200,
    )


@comments_bp.route("/comments/<comment_id>", methods=["PUT"])
def update_comment(comment_id):
    """
    Update the text content of an existing comment.
    Expected JSON body:
        { "content": "<new text>" }

    Responses:
        200 with updated content on success,
        400 if 'content' is missing or id is invalid,
        404 if comment does not exist.
    """
    payload = request.get_json(silent=True) or {}
    content = payload.get("content")

    if content is None:
        return jsonify({"error": "Field 'content' is required."}), 400

    db = get_database()
    try:
        result = db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {"content": content, "updated_at": datetime.utcnow()}},
        )
    except Exception:
        return jsonify({"error": "Comment id is invalid."}), 400

    if result.matched_count == 0:
        return jsonify({"error": "Comment not found."}), 404

    return jsonify({"id": comment_id, "content": content}), 200


@comments_bp.route("/comments/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    """
    Delete a comment by ID.
    Returns:
        204 on success (empty body),
        400 for invalid id,
        404 if comment not found.
    """
    db = get_database()
    try:
        result = db.comments.delete_one({"_id": ObjectId(comment_id)})
    except Exception:
        return jsonify({"error": "Comment id is invalid."}), 400

    if result.deleted_count == 0:
        return jsonify({"error": "Comment not found."}), 404

    return jsonify({}), 204
