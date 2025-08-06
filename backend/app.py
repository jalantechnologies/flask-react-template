from flask import Flask, render_template
from extensions import db
from models.comment import Comment
from routes.comment_routes import comment_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(comment_bp, url_prefix="/comments")

    # Frontend route
    @app.route('/')
    def index():
        return render_template("index.html")

    # Create tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

