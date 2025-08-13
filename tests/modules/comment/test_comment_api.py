from server import app

from tests.modules.comment.base_test_comment import BaseTestComment


class TestCommentApi(BaseTestComment):

    def test_create_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT, "author_name": self.DEFAULT_AUTHOR_NAME}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        assert response.status_code == 201
        assert response.json is not None
        self.assert_comment_response(
            response.json,
            content=self.DEFAULT_COMMENT_CONTENT,
            author_name=self.DEFAULT_AUTHOR_NAME,
            task_id=task.id,
            account_id=account.id,
        )

    def test_create_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"author_name": self.DEFAULT_AUTHOR_NAME}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        self.assert_error_response(response, 400, "Content is required")

    def test_create_comment_missing_author_name(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        self.assert_error_response(response, 400, "Author name is required")

    def test_create_comment_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        self.assert_error_response(response, 400, "Content is required")

    def test_create_comment_empty_content_string(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": "   ", "author_name": self.DEFAULT_AUTHOR_NAME}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        self.assert_error_response(response, 400, "Content must be a non-empty string")

    def test_create_comment_empty_author_name_string(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT, "author_name": "   "}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        self.assert_error_response(response, 400, "Author name must be a non-empty string")

    def test_create_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": self.DEFAULT_COMMENT_CONTENT, "author_name": self.DEFAULT_AUTHOR_NAME}

        response = self.make_unauthenticated_request("POST", account.id, task.id, data=comment_data)

        self.assert_error_response(response, 401)

    def test_get_all_comments_empty(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_authenticated_request("GET", account.id, token, task.id)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=0, expected_total_count=0)

    def test_get_all_comments_with_comments(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comments = self.create_multiple_test_comments(task_id=task.id, account_id=account.id, count=3)

        response = self.make_authenticated_request("GET", account.id, token, task.id)

        assert response.status_code == 200
        self.assert_pagination_response(response.json, expected_items_count=3, expected_total_count=3)

        # Verify comments are returned (they come in reverse order due to default sorting)
        assert len(response.json["items"]) == 3
        for i, comment in enumerate(response.json["items"]):
            assert comment["content"] == f"Comment {3-i}"
            assert comment["author_name"] == f"Author {3-i}"

    def test_get_all_comments_with_pagination(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        self.create_multiple_test_comments(task_id=task.id, account_id=account.id, count=5)

        response1 = self.make_authenticated_request("GET", account.id, token, task.id, query_params="page=1&size=2")
        response2 = self.make_authenticated_request("GET", account.id, token, task.id, query_params="page=2&size=2")

        assert response1.status_code == 200
        self.assert_pagination_response(
            response1.json, expected_items_count=2, expected_total_count=5, expected_page=1, expected_size=2
        )

        assert response2.status_code == 200
        self.assert_pagination_response(
            response2.json, expected_items_count=2, expected_total_count=5, expected_page=2, expected_size=2
        )

        # Verify different comments on different pages
        assert response1.json["items"][0]["id"] != response2.json["items"][0]["id"]

    def test_get_all_comments_with_sorting(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        self.create_multiple_test_comments(task_id=task.id, account_id=account.id, count=3)

        # Test ascending order
        response_asc = self.make_authenticated_request(
            "GET", account.id, token, task.id, query_params="sort_by=created_at&sort_order=asc"
        )
        # Test descending order (default)
        response_desc = self.make_authenticated_request(
            "GET", account.id, token, task.id, query_params="sort_by=created_at&sort_order=desc"
        )

        assert response_asc.status_code == 200
        assert response_desc.status_code == 200

        # Both should return the same number of comments
        assert len(response_asc.json["items"]) == 3
        assert len(response_desc.json["items"]) == 3

    def test_get_all_comments_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)

        response = self.make_unauthenticated_request("GET", account.id, task.id)

        self.assert_error_response(response, 401)

    def test_get_specific_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(task_id=task.id, account_id=account.id)

        response = self.make_authenticated_request("GET", account.id, token, task.id, comment_id=created_comment.id)

        assert response.status_code == 200
        self.assert_comment_response(response.json, expected_comment=created_comment)

    def test_get_specific_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request(
            "GET", account.id, token, task.id, comment_id=non_existent_comment_id
        )

        self.assert_error_response(response, 400)

    def test_get_specific_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_unauthenticated_request("GET", account.id, task.id, comment_id=fake_comment_id)

        self.assert_error_response(response, 401)

    def test_update_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(
            task_id=task.id, account_id=account.id, content="Original Content", author_name="Original Author"
        )
        update_data = {"content": "Updated Content"}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task.id, comment_id=created_comment.id, data=update_data
        )

        assert response.status_code == 200
        self.assert_comment_response(
            response.json,
            id=created_comment.id,
            task_id=task.id,
            account_id=account.id,
            content="Updated Content",
            author_name="Original Author",  # Should remain unchanged
        )

    def test_update_comment_missing_content(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(task_id=task.id, account_id=account.id)
        update_data = {}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task.id, comment_id=created_comment.id, data=update_data
        )

        self.assert_error_response(response, 400, "Content is required")

    def test_update_comment_empty_content_string(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(task_id=task.id, account_id=account.id)
        update_data = {"content": "   "}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task.id, comment_id=created_comment.id, data=update_data
        )

        self.assert_error_response(response, 400, "Content must be a non-empty string")

    def test_update_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"content": "Updated Content"}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task.id, comment_id=non_existent_comment_id, data=update_data
        )

        self.assert_error_response(response, 400)

    def test_update_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"
        update_data = {"content": "Updated Content"}

        response = self.make_unauthenticated_request(
            "PATCH", account.id, task.id, comment_id=fake_comment_id, data=update_data
        )

        self.assert_error_response(response, 401)

    def test_delete_comment_success(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(
            task_id=task.id, account_id=account.id, content="Comment to Delete", author_name="Author to Delete"
        )

        delete_response = self.make_authenticated_request(
            "DELETE", account.id, token, task.id, comment_id=created_comment.id
        )

        assert delete_response.status_code == 200
        assert delete_response.json is not None
        assert delete_response.json.get("success") is True
        assert delete_response.json.get("comment_id") == created_comment.id
        assert delete_response.json.get("deleted_at") is not None

        # Verify comment is no longer accessible
        get_response = self.make_authenticated_request("GET", account.id, token, task.id, comment_id=created_comment.id)
        assert get_response.status_code == 400  # Comment should be soft deleted

    def test_delete_comment_not_found(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        non_existent_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_authenticated_request(
            "DELETE", account.id, token, task.id, comment_id=non_existent_comment_id
        )

        self.assert_error_response(response, 400)

    def test_delete_comment_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        fake_comment_id = "507f1f77bcf86cd799439011"

        response = self.make_unauthenticated_request("DELETE", account.id, task.id, comment_id=fake_comment_id)

        self.assert_error_response(response, 401)

    def test_comments_are_account_isolated_via_api(self) -> None:
        account1, token1 = self.create_account_and_get_token("user1@example.com", "password1")
        account2, token2 = self.create_account_and_get_token("user2@example.com", "password2")

        # Create task and comment for account1
        task1 = self.create_test_task(account_id=account1.id)
        comment_data = {"content": "Account 1 Comment", "author_name": "Account 1 Author"}
        create_response = self.make_authenticated_request("POST", account1.id, token1, task1.id, data=comment_data)
        account1_comment_id = create_response.json.get("id")

        # Try to access account1's comment with account2's token
        get_response = self.make_cross_account_request(
            "GET", account1.id, token2, task1.id, comment_id=account1_comment_id
        )
        patch_response = self.make_cross_account_request(
            "PATCH", account1.id, token2, task1.id, comment_id=account1_comment_id, data={"content": "Hacked"}
        )
        delete_response = self.make_cross_account_request(
            "DELETE", account1.id, token2, task1.id, comment_id=account1_comment_id
        )

        # All should fail with unauthorized access
        self.assert_error_response(get_response, 401)
        self.assert_error_response(patch_response, 401)
        self.assert_error_response(delete_response, 401)

        # Verify comment is still accessible by account1
        verify_response = self.make_authenticated_request(
            "GET", account1.id, token1, task1.id, comment_id=account1_comment_id
        )
        assert verify_response.status_code == 200
        assert verify_response.json.get("id") == account1_comment_id

    def test_comments_are_task_isolated(self) -> None:
        account, token = self.create_account_and_get_token()
        task1 = self.create_test_task(account_id=account.id, title="Task 1")
        task2 = self.create_test_task(account_id=account.id, title="Task 2")

        # Create comment for task1
        comment_data = {"content": "Task 1 Comment", "author_name": "Task 1 Author"}
        create_response = self.make_authenticated_request("POST", account.id, token, task1.id, data=comment_data)
        task1_comment_id = create_response.json.get("id")

        # Try to access task1's comment via task2's endpoint
        get_response = self.make_authenticated_request("GET", account.id, token, task2.id, comment_id=task1_comment_id)

        # Should fail as comment belongs to different task
        self.assert_error_response(get_response, 400)

    def test_invalid_json_request_body(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        invalid_json_data = "invalid json"

        with app.test_client() as client:
            response = client.post(
                self.get_comment_api_url(account.id, task.id),
                headers={**self.HEADERS, "Authorization": f"Bearer {token}"},
                data=invalid_json_data,
            )

        self.assert_error_response(response, 400)

    def test_create_comment_with_whitespace_trimming(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        comment_data = {"content": "  Content with whitespace  ", "author_name": "  Author with whitespace  "}

        response = self.make_authenticated_request("POST", account.id, token, task.id, data=comment_data)

        assert response.status_code == 201
        assert response.json is not None
        # Verify whitespace is trimmed
        assert response.json.get("content") == "Content with whitespace"
        assert response.json.get("author_name") == "Author with whitespace"

    def test_update_comment_with_whitespace_trimming(self) -> None:
        account, token = self.create_account_and_get_token()
        task = self.create_test_task(account_id=account.id)
        created_comment = self.create_test_comment(task_id=task.id, account_id=account.id)
        update_data = {"content": "  Updated content with whitespace  "}

        response = self.make_authenticated_request(
            "PATCH", account.id, token, task.id, comment_id=created_comment.id, data=update_data
        )

        assert response.status_code == 200
        # Verify whitespace is trimmed
        assert response.json.get("content") == "Updated content with whitespace"
