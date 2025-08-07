# flask tools for the server
from flask import Flask, jsonify, request
from flask_cors import CORS
# for unique IDs and timestamps
import uuid
from datetime import datetime

# set up the main app
app = Flask(__name__)
CORS(app)

# using a simple dict as a temporary db
_comments_db = {}


# --- Main route for getting all comments or posting a new one ---
@app.route("/api/comments/for-task/<task_id>", methods=["POST", "GET"])
def handle_comments_for_task(task_id):
    # For testing, we'll use a hardcoded user ID
    user_id = "frontend-user"

    # if it's a POST, we're making a new comment
    if request.method == "POST":
        payload = request.get_json()
        if not payload or 'text' not in payload:
            return jsonify({"error": "missing text"}), 400

        new_comment = {
            "id": str(uuid.uuid4()),
            "author_id": user_id,
            "text": payload["text"],
            "created_at": datetime.now().isoformat() + "Z",
        }

        if task_id not in _comments_db:
            _comments_db[task_id] = []
        
        _comments_db[task_id].append(new_comment)
        return jsonify(new_comment), 201
    
    # otherwise, it's a GET, so just send back the comments
    else:
        comments = _comments_db.get(task_id, [])
        return jsonify(comments)


# --- Route for dealing with one specific comment (update or delete) ---
@app.route("/api/comments/<comment_id>", methods=["PUT", "DELETE"])
def handle_specific_comment(comment_id):
    user_id = "frontend-user"

    comment = None
    task_id = None
    for tid, comments in _comments_db.items():
        for c in comments:
            if c["id"] == comment_id:
                comment = c
                task_id = tid
                break
        if comment:
            break

    if not comment:
        return jsonify({"error": "comment not found"}), 404

    if comment["author_id"] != user_id:
        return jsonify({"error": "permission denied"}), 403

    if request.method == "PUT":
        payload = request.get_json()
        if not payload or 'text' not in payload:
            return jsonify({"error": "missing new text"}), 400
        
        comment["text"] = payload["text"]
        return jsonify(comment)
    
    elif request.method == "DELETE":
        comments_list = _comments_db[task_id]
        _comments_db[task_id] = [c for c in comments_list if c["id"] != comment_id]
        return '', 204