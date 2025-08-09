import unittest
from app import app, comments  # Import the comments list

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        global comments
        comments.clear()  # Clear the comments list after each test

    def test_add_comment(self):
        response = self.app.post('/comments', json={"task_id": 1, "content": "Test comment"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)

    def test_get_comments(self):
        # Add only one comment for this test
        self.app.post('/comments', json={"task_id": 1, "content": "Test comment"})
        response = self.app.get('/comments?task_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)  # Ensure only one comment is returned

    def test_edit_comment(self):
        self.app.post('/comments', json={"task_id": 1, "content": "Test comment"})
        response = self.app.put('/comments/1', json={"content": "Updated comment"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["content"], "Updated comment")

    def test_delete_comment(self):
        self.app.post('/comments', json={"task_id": 1, "content": "Test comment"})
        response = self.app.delete('/comments/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Comment deleted")

if _name_ == '_main_':
    unittest.main()