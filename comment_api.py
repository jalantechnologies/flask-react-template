from flask import Flask, request, jsonify

app = Flask(__name__)

comments = []
next_id = 1

@app.route("/comments", methods=["POST"])
def add_comment():
    global next_id
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "Comment text is required"}), 400

    comment = {"id": next_id, "text": text}
    comments.append(comment)
    next_id += 1
    return jsonify(comment), 201

@app.route("/comments/<int:comment_id>", methods=["PUT"])
def edit_comment(comment_id):
    data = request.get_json()
    text = data.get("text")
    for comment in comments:
        if comment["id"] == comment_id:
            comment["text"] = text
            return jsonify(comment)
    return jsonify({"error": "Comment not found"}), 404

@app.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    global comments
    for comment in comments:
        if comment["id"] == comment_id:
            comments = [c for c in comments if c["id"] != comment_id]
            return jsonify({"message": "Deleted"})
    return jsonify({"error": "Comment not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
