
from flask import Flask
from extensions import db, migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# ✅ import models AFTER init_app
from models.task import Task
from models.comment import Comment

# ✅ register blueprints AFTER model import
from routes.task_routes import task_bp
from routes.comment_routes import comment_bp

app.register_blueprint(task_bp)
app.register_blueprint(comment_bp)

@app.route('/')
def home():
    return "Flask DB works!"
