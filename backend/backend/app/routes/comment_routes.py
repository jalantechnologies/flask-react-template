from flask import Blueprint, request, jsonify

comment_bp = Blueprint('comment_bp', __name__)

comments = []
next_id = 1  # To assign unique IDs


# @comment_bp.route('/comments', methods=['GET', 'POST'])
# def comments_handler():
#     if request.method == 'POST':
#         data = request.get_json()
#         comment = data.get('comment')
#         if comment:
#             comments.append(comment)
#             return jsonify({"message": "Comment added"}), 201
#         return jsonify({"error": "No comment provided"}), 400
#     return jsonify(comments), 200



@comment_bp.route('/comments', methods=['GET', 'POST'])
def comments_handler():
    global next_id
    if request.method == 'POST':
        data = request.get_json()
        comment_text = data.get('comment')
        if comment_text:
            comment_obj = {
                "id": next_id,
                "content": comment_text
            }
            comments.append(comment_obj)
            next_id += 1
            return jsonify(comment_obj), 201
        return jsonify({"error": "No comment provided"}), 400
    return jsonify(comments), 200


@comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    global comments
    comments = [c for c in comments if c["id"] != comment_id]
    return jsonify({"message": "Comment deleted"}), 200

@comment_bp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.get_json()
    new_content = data.get('comment')

    for comment in comments:
        if comment["id"] == comment_id:
            comment["content"] = new_content
            return jsonify(comment), 200

    return jsonify({"error": "Comment not found"}), 404

