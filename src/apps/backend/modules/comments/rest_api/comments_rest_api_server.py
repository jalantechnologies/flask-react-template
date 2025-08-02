from flask import Blueprint

from .comments_router import create_route


def create() -> Blueprint:
    bp = Blueprint("comments", __name__)
    return create_route(blueprint=bp)
