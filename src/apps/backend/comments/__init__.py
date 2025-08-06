from flask import Blueprint
from .routes import register_routes

comments_bp = Blueprint('comments', __name__)
register_routes(comments_bp)

