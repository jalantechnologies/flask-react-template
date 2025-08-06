from flask import request, jsonify
from .service import CommentService

def register_routes(bp):
    @bp.route('/comments', methods=['POST'])
    def create_comment():
        data = request.get_json()
        comment = CommentService.create_comment(data)
        return jsonify(comment), 201

    @bp.route('/comments/<int:comment_id>', methods=['GET'])
    def get_comment(comment_id):
       comment = CommentService.get_comment(comment_id)
       if comment:
          return jsonify(comment)
       return jsonify({"error": "Comment not found"}), 404


    @bp.route('/comments/<int:comment_id>', methods=['PUT'])
    def update_comment(comment_id):
        data = request.get_json()
        comment = CommentService.update_comment(comment_id, data)
        return jsonify(comment)

    @bp.route('/comments/<int:comment_id>', methods=['DELETE'])
    def delete_comment(comment_id):
        CommentService.delete_comment(comment_id)
        return jsonify({"message": "Comment deleted"})
