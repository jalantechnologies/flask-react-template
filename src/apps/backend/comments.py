from flask import Blueprint, request, jsonify

comments_bp = Blueprint('comments', __name__)

# Temporary in-memory comment store
comments = {}
comment_id_counter = 1

@comments_bp.route('/comments', methods=['POST'])
def add_comment():


    global comment_id_counter
    data = request.get_json()
    comment = {
        "id": comment_id_counter,
        "task_id": data['task_id'],
        "text": data['text']
    }
    comments[comment_id_counter] = comment
    comment_id_counter += 1
    return jsonify(comment), 201

@comments_bp.route('/comments/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    if comment_id not in comments:
        return jsonify({"error": "Comment not found"}), 404
    data = request.get_json()
    comments[comment_id]['text'] = data['text']
    return jsonify(comments[comment_id])

@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    if comment_id not in comments:
        return jsonify({"error": "Comment not found"}), 404
    del comments[comment_id]
    return jsonify({"message": "Deleted successfully"}), 200

@comments_bp.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    if comment_id not in comments:
        return jsonify({"error": "Comment not found"}), 404
    return jsonify(comments[comment_id])
