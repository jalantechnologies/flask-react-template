from .comments_view import CommentsView


def create_route(blueprint):
    view = CommentsView.as_view("comments_view")

    blueprint.add_url_rule("/tasks/<task_id>/comments", view_func=view, methods=["GET", "POST"])

    blueprint.add_url_rule("/tasks/<task_id>/comments/<comment_id>", view_func=view, methods=["GET", "PATCH", "DELETE"])

    return blueprint
