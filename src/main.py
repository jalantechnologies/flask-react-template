# src/main.py
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import mongomock

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    CORS(app)

    if test_config:
        app.config.update(test_config)
    else:
        app.config.setdefault("MONGO_URI", "mongodb://localhost:27017")
        app.config.setdefault("MONGO_DBNAME", "flaskreact")

    # Try connecting to a real MongoDB; if it fails, use mongomock
    try:
        client = MongoClient(
            app.config["MONGO_URI"], serverSelectionTimeoutMS=1000
        )
        client.server_info()  # Force a connection test
        print("✅ Connected to real MongoDB server.")
    except Exception:
        print("⚠️  No MongoDB detected — using in-memory mongomock client.")
        client = mongomock.MongoClient()

    app.config["MONGO_CLIENT"] = client
    app.config["MONGO_DBNAME"] = app.config.get("MONGO_DBNAME", "flaskreact")

    from src.api.comments import comments_bp
    app.register_blueprint(comments_bp)

    @app.route("/health")
    def health():
        return {"ok": True}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5555, debug=True, use_reloader=False)

