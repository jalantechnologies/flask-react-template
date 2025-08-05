import unittest
import json
from comment_api import app

class CommentApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_add_comment(self):
        response = self.app.post('/comments', json={"text": "Test comment"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("Test comment", response.get_data(as_text=True))

    def test_get_comments(self):
        # Add a comment first so the list is not empty
        self.app.post('/comments', json={"text": "Another comment"})
        
        response = self.app.get('/comments')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_update_comment(self):
        # First add a comment to update
        post_resp = self.app.post('/comments', json={"text": "Old comment"})
        comment_id = post_resp.get_json()["id"]

        # Now update it
        response = self.app.put(f'/comments/{comment_id}', json={"text": "Updated comment"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Updated comment", response.get_data(as_text=True))

    def test_delete_comment(self):
        # First add a comment to delete
        post_resp = self.app.post('/comments', json={"text": "Delete me"})
        comment_id = post_resp.get_json()["id"]

        # Now delete it
        response = self.app.delete(f'/comments/{comment_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Deleted", response.get_data(as_text=True))  # Capital "D" to match actual response

if __name__ == '__main__':
    unittest.main()
