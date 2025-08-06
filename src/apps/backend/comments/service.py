class CommentService:
    comments = []
    next_id = 1

    @classmethod
    def create_comment(cls, data):
        comment = {
            'id': cls.next_id,
            'author': data.get('author'),
            'content': data.get('content')
        }
        cls.comments.append(comment)
        cls.next_id += 1
        return comment

    @classmethod
    def get_comment(cls, comment_id):
        for comment in cls.comments:
            if comment['id'] == comment_id:
                return comment
        return {'error': 'Comment not found'}, 404

    @classmethod
    def update_comment(cls, comment_id, data):
        for comment in cls.comments:
            if comment['id'] == comment_id:
                comment.update({
                    'author': data.get('author', comment['author']),
                    'content': data.get('content', comment['content']),
                })
                return comment
        return {'error': 'Comment not found'}, 404

    @classmethod
    def delete_comment(cls, comment_id):
        for comment in cls.comments:
            if comment['id'] == comment_id:
                cls.comments.remove(comment)
                return
        return {'error': 'Comment not found'}, 404
