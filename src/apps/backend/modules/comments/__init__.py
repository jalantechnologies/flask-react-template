from flask import Blueprint

comments_blueprint = Blueprint('comments', __name__, url_prefix='/api/comments')

from . import routes
