import pytest
from run import app as flask_app

from modules.common.flask.extensions import db  # ✅ Updated import path
from modules.account.models import User
from modules.task.models import Task

@pytest.fixture
def client():
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["TESTING"] = True

    with flask_app.app_context():
        db.create_all()

        # Add dummy user and task
        user = User(id=1, name="Test User", email="test@example.com")
        task = Task(id=1, title="Test Task", description="For testing")
        db.session.add(user)
        db.session.add(task)
        db.session.commit()

    with flask_app.test_client() as client:
        yield client

    # Optional teardown
    with flask_app.app_context():
        db.drop_all()
