from flask import Flask, jsonify
from flask_cors import CORS
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comments.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app, origins=["http://localhost:3000"])

    from app.routes.comment_routes import comment_bp
    app.register_blueprint(comment_bp, url_prefix="/api")

    # Root route to show status message
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({"message": "Flask backend app is running"}), 200

    return app
