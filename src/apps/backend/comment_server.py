# flask tools for the server
from flask import Flask, jsonify, request
from flask_cors import CORS # 👈 New import for CORS
# for unique IDs and timestamps
import uuid
from datetime import datetime

# set up the main app
app = Flask(__name__)
CORS(app) # 👈 New line to enable CORS

# using a simple dict as a temporary db
# NOTE: this will get wiped if the server restarts
_comments_db = {}


# --- Main route for getting all comments or posting a new one ---
@app.route("/api/comments/for-task/<task_id>", methods=["POST", "GET"])
def handle_comments_for_task(task_id):
    # if it's a POST, we're making a new comment
    if request.method == "POST":
        payload = request.get_json()

        # quick check to make sure we got what we need
        if not payload or 'text' not in payload or 'author_id' not in payload:
            return jsonify({"error": "missing text or author_id"}), 400

        # alright, let's build the comment
        new_comment = {
            "id": str(uuid.uuid4()),
            "author_id": payload["author_id"],
            "text": payload["text"],
            "created_at": datetime.now().isoformat() + "Z", # Using datetime.now() with UTC as suggested by the test warnings
        }

        # if the task isn't in our db yet, add it
        if task_id not in _comments_db:
            _comments_db[task_id] = []
        
        _comments_db[task_id].append(new_comment)

        # send back the comment we just made, with a 201 'Created' status
        return jsonify(new_comment), 201
    
    # otherwise, it's a GET, so just send back the comments
    else:
        # .get() is safer, returns an empty list if the task_id isn't found
        comments = _comments_db.get(task_id, [])
        return jsonify(comments)


# --- Route for dealing with one specific comment (update or delete) ---
@app.route("/api/comments/<comment_id>", methods=["PUT", "DELETE"])
def handle_specific_comment(comment_id):
    # if it's a PUT, we're updating
    if request.method == "PUT":
        payload = request.get_json()
        if not payload or 'text' not in payload:
            return jsonify({"error": "missing new text"}), 400

        # gotta find the comment first
        for task_comments in _comments_db.values():
            for comment in task_comments:
                if comment["id"] == comment_id:
                    # found it, update the text
                    comment["text"] = payload["text"]
                    return jsonify(comment) # send back the updated comment
        
        # if we get here, we didn't find it
        return jsonify({"error": "comment not found"}), 404

    # if it's a DELETE, we're getting rid of it
    elif request.method == "DELETE":
        # loop through a copy of the items to safely delete
        for task_id, comments in list(_comments_db.items()):
            # find the index of the comment to remove
            for i, comment in enumerate(comments):
                if comment["id"] == comment_id:
                    # remove it from the list
                    del _comments_db[task_id][i]
                    # send back an empty response, 204 means 'No Content'
                    return '', 204
        
        # if we get here, we didn't find it
        return jsonify({"error": "comment not found"}), 404