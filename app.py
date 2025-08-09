from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for simplicity
comments = []

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Comments API. Use the /comments endpoint to interact with the API."})

@app.route('/comments', methods=['POST'])
def add_comment():
    data = request.json
    if not data or "task_id" not in data or "content" not in data:
        return jsonify({"error": "Invalid input. 'task_id' and 'content' are required."}), 400
    if not isinstance(data["task_id"], int) or not isinstance(data["content"], str) or not data["content"].strip():
        return jsonify({"error": "Invalid input. 'task_id' must be an integer and 'content' must be a non-empty string."}), 400

    comment = {
        "id": len(comments) + 1,
        "task_id": data["task_id"],
        "content": data["content"]
    }
    comments.append(comment)
    return jsonify(comment), 201

@app.route('/comments/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    data = request.json
    if not data or "content" not in data:
        return jsonify({"error": "Invalid input. 'content' is required."}), 400
    if not isinstance(data["content"], str) or not data["content"].strip():
        return jsonify({"error": "Invalid input. 'content' must be a non-empty string."}), 400

    for comment in comments:
        if comment["id"] == comment_id:
            comment["content"] = data["content"]
            return jsonify(comment), 200  # Return the updated comment with status code 200

    return jsonify({"error": "Comment not found"}), 404

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    global comments
    comment_exists = any(c["id"] == comment_id for c in comments)
    if not comment_exists:
        return jsonify({"error": "Comment not found"}), 404

    comments = [c for c in comments if c["id"] != comment_id]
    return jsonify({"message": "Comment deleted"}), 200

@app.route('/comments', methods=['GET'])
def get_comments():
    task_id = request.args.get("task_id")
    if not task_id:
        return jsonify({"error": "Invalid input. 'task_id' is required as a query parameter."}), 400
    try:
        task_id = int(task_id)
    except ValueError:
        return jsonify({"error": "Invalid input. 'task_id' must be an integer."}), 400

    task_comments = [c for c in comments if c["task_id"] == task_id]
    return jsonify(task_comments)

if __name__ == '__main__':
    app.run(debug=True)