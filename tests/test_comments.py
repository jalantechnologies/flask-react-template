import pytest
from app import app, db
from models.comment import Comment

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

# ✅ Auto fixture to reset DB
@pytest.fixture(autouse=True)
def run_before_each_test():
    with app.app_context():
        db.drop_all()
        db.create_all()

def test_create_comment(client):
    res = client.post('/api/comments', json={'task_id': 1, 'content': 'Test comment'})
    assert res.status_code == 201
    assert 'id' in res.get_json()

def test_get_comments(client):
    with app.app_context():
        comment = Comment(task_id=1, content='Sample comment')
        db.session.add(comment)
        db.session.commit()

    res = client.get('/api/comments/task/1')
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)
    assert res.get_json()[0]['content'] == 'Sample comment'

def test_update_comment(client):
    with app.app_context():
        comment = Comment(task_id=1, content='Old comment')
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    res = client.put(f'/api/comments/{comment_id}', json={'content': 'Updated'})
    assert res.status_code == 200
    assert res.get_json()['message'] == 'Comment updated'

def test_delete_comment(client):
    with app.app_context():
        comment = Comment(task_id=1, content='To delete')
        db.session.add(comment)
        db.session.commit()
        comment_id = comment.id

    res = client.delete(f'/api/comments/{comment_id}')
    assert res.status_code == 200
    assert res.get_json()['message'] == 'Comment deleted'
