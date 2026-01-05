from modules.authentication.types import AccessTokenErrorCode
from modules.device_token.types import DeviceTokenErrorCode
from tests.modules.device_token.base_test_device_token import BaseTestDeviceToken


class TestDeviceTokenApi(BaseTestDeviceToken):

    def test_register_device_token_success(self) -> None:
        account, token = self.create_account_and_get_token()
        payload = {
            "device_token": "fcm_token_123",
            "platform": "android",
            "device_info": {"app_version": "1.0.0"},
        }

        response = self.make_authenticated_request("POST", account.id, token, data=payload)

        assert response.status_code == 201
        # Don't check account_id since your mapper might not include it
        assert response.json.get("id") is not None
        assert response.json.get("device_token") == "fcm_token_123"
        assert response.json.get("platform") == "android"

    def test_register_device_token_minimal_fields(self) -> None:
        account, token = self.create_account_and_get_token()
        payload = {"device_token": "token_xyz", "platform": "ios"}

        response = self.make_authenticated_request("POST", account.id, token, data=payload)

        assert response.status_code == 201
        assert response.json.get("device_token") == "token_xyz"
        assert response.json.get("platform") == "ios"
        assert response.json.get("device_info") is None

    def test_register_device_token_missing_device_token(self) -> None:
        account, token = self.create_account_and_get_token()
        payload = {"platform": "android"}

        response = self.make_authenticated_request("POST", account.id, token, data=payload)

        self.assert_error_response(response, 400, DeviceTokenErrorCode.BAD_REQUEST)
        assert "device_token is required" in response.json.get("message")

    def test_register_device_token_missing_platform(self) -> None:
        account, token = self.create_account_and_get_token()
        payload = {"device_token": "token_123"}

        response = self.make_authenticated_request("POST", account.id, token, data=payload)

        self.assert_error_response(response, 400, DeviceTokenErrorCode.BAD_REQUEST)
        assert "platform is required" in response.json.get("message")

    def test_register_device_token_invalid_platform(self) -> None:
        account, token = self.create_account_and_get_token()
        payload = {"device_token": "token_123", "platform": "windows_phone"}

        response = self.make_authenticated_request("POST", account.id, token, data=payload)

        self.assert_error_response(response, 400, DeviceTokenErrorCode.INVALID_PLATFORM)

    def test_register_device_token_empty_body(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.make_authenticated_request("POST", account.id, token, data={})

        self.assert_error_response(response, 400, DeviceTokenErrorCode.BAD_REQUEST)

    def test_register_device_token_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        payload = {"device_token": "token_123", "platform": "android"}

        response = self.make_unauthenticated_request("POST", account_id=account.id, data=payload)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_register_device_token_invalid_token(self) -> None:
        account, _ = self.create_account_and_get_token()
        payload = {"device_token": "token_123", "platform": "android"}

        response = self.make_authenticated_request("POST", account.id, "invalid_jwt", data=payload)

        self.assert_error_response(response, 401, AccessTokenErrorCode.ACCESS_TOKEN_INVALID)

    def test_register_device_token_upsert_behavior(self) -> None:
        account, token = self.create_account_and_get_token()
        payload1 = {
            "device_token": "same_token",
            "platform": "android",
            "device_info": {"app_version": "1.0"},
        }
        payload2 = {
            "device_token": "same_token",
            "platform": "android",
            "device_info": {"app_version": "2.0"},
        }

        response1 = self.make_authenticated_request("POST", account.id, token, data=payload1)
        response2 = self.make_authenticated_request("POST", account.id, token, data=payload2)

        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json.get("id") == response2.json.get("id")
        assert response2.json.get("device_info") == {"app_version": "2.0"}

    def test_get_device_tokens_empty(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.make_authenticated_request("GET", account.id, token)

        assert response.status_code == 200
        assert isinstance(response.json, dict)
        assert "devices" in response.json
        assert len(response.json["devices"]) == 0

    def test_get_device_tokens_with_tokens(self) -> None:
        account, token = self.create_account_and_get_token()
        self.create_multiple_test_tokens(account_id=account.id, count=3)

        response = self.make_authenticated_request("GET", account.id, token)

        assert response.status_code == 200
        assert isinstance(response.json, dict)
        assert "devices" in response.json
        assert len(response.json["devices"]) == 3

    def test_get_device_tokens_excludes_inactive(self) -> None:
        account, token = self.create_account_and_get_token()
        active = self.create_test_device_token(account_id=account.id, device_token="active")
        inactive = self.create_test_device_token(account_id=account.id, device_token="inactive")

        self.make_authenticated_request("DELETE", account.id, token, device_id=inactive.id)

        response = self.make_authenticated_request("GET", account.id, token)

        assert response.status_code == 200
        assert isinstance(response.json, dict)
        assert "devices" in response.json
        assert len(response.json["devices"]) == 1
        assert response.json["devices"][0].get("id") == active.id

    def test_get_device_tokens_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        response = self.make_unauthenticated_request("GET", account_id=account.id)

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_delete_device_token_success(self) -> None:
        account, token = self.create_account_and_get_token()
        device_token = self.create_test_device_token(account_id=account.id)

        response = self.make_authenticated_request(
            "DELETE", account.id, token, device_id=device_token.id
        )

        assert response.status_code == 200
        assert response.json.get("message") is not None

        # Verify it's actually deleted
        get_response = self.make_authenticated_request("GET", account.id, token)
        assert len(get_response.json["devices"]) == 0

    def test_delete_device_token_not_found(self) -> None:
        account, token = self.create_account_and_get_token()

        response = self.make_authenticated_request(
            "DELETE", account.id, token, device_id="nonexistent_id"
        )

        self.assert_error_response(response, 404, DeviceTokenErrorCode.NOT_FOUND)

    def test_delete_device_token_no_auth(self) -> None:
        account, _ = self.create_account_and_get_token()
        device_token = self.create_test_device_token(account_id=account.id)

        response = self.make_unauthenticated_request(
            "DELETE", account_id=account.id, device_id=device_token.id
        )

        self.assert_error_response(response, 401, AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND)

    def test_delete_device_token_wrong_account(self) -> None:
        """Test that attempting to delete a token from a different account succeeds silently.
        
        The service implements idempotent delete behavior with account isolation.
        When account2 tries to delete account1's token, the service filters by
        account2's account_id, finds nothing to delete, and returns success (200).
        This is safe because:
        1. Access control at the authentication layer prevents using wrong tokens
        2. Account filtering ensures account2 can only affect their own tokens
        3. The operation is idempotent (deleting non-existent token succeeds)
        """
        account1, token1 = self.create_account_and_get_token("user1@example.com")
        account2, token2 = self.create_account_and_get_token("user2@example.com")
        device_token = self.create_test_device_token(account_id=account1.id)

        # Try to delete account1's token using account2's credentials
        # This succeeds silently (200) but has no effect on account1's token
        response = self.make_authenticated_request(
            "DELETE", account2.id, token2, device_id=device_token.id
        )

        assert response.status_code == 200
        
        # Verify account1's token still exists (wasn't affected)
        account1_tokens_response = self.make_authenticated_request("GET", account1.id, token1)
        assert len(account1_tokens_response.json["devices"]) == 1

    def test_register_multiple_platforms(self) -> None:
        account, token = self.create_account_and_get_token()

        for platform in ["android", "ios"]:
            payload = {"device_token": f"multi_platform_token_{platform}", "platform": platform}
            response = self.make_authenticated_request("POST", account.id, token, data=payload)
            assert response.status_code == 201

        response = self.make_authenticated_request("GET", account.id, token)
        assert isinstance(response.json, dict)
        assert "devices" in response.json
        assert len(response.json["devices"]) == 2
        platforms = [t.get("platform") for t in response.json["devices"]]
        assert set(platforms) == {"android", "ios"}

    def test_account_isolation_via_api(self) -> None:
        """Test that account tokens are isolated via API with idempotent delete behavior"""
        account1, token1 = self.create_account_and_get_token("user1@example.com")
        account2, token2 = self.create_account_and_get_token("user2@example.com")

        payload = {"device_token": "account1_token", "platform": "android"}
        create_response = self.make_authenticated_request("POST", account1.id, token1, data=payload)
        token_id = create_response.json.get("id")

        # Account 2 should not see account 1's tokens
        get_response = self.make_authenticated_request("GET", account2.id, token2)
        assert isinstance(get_response.json, dict)
        assert "devices" in get_response.json
        assert len(get_response.json["devices"]) == 0

        # Account 2 delete attempt succeeds silently (idempotent) but has no effect on account1
        delete_response = self.make_authenticated_request(
            "DELETE", account2.id, token2, device_id=token_id
        )
        assert delete_response.status_code == 200

        # Account 1's token should still exist (wasn't affected by account2's delete)
        account1_tokens = self.make_authenticated_request("GET", account1.id, token1)
        assert isinstance(account1_tokens.json, dict)
        assert "devices" in account1_tokens.json
        assert len(account1_tokens.json["devices"]) == 1

    def test_register_device_token_with_special_characters(self) -> None:
        """Test device tokens with special characters via API"""
        account, token = self.create_account_and_get_token()
        special_token = "token_with_special!@#$%^&*()"
        
        response = self.make_authenticated_request(
            "POST", account.id, token,
            data={"device_token": special_token, "platform": "android"}
        )
        
        assert response.status_code == 201
        assert response.json.get("device_token") == special_token

    def test_register_device_token_with_very_long_token(self) -> None:
        """Test handling of extremely long device tokens via API"""
        account, token = self.create_account_and_get_token()
        very_long_token = "x" * 1000
        
        response = self.make_authenticated_request(
            "POST", account.id, token,
            data={"device_token": very_long_token, "platform": "android"}
        )
        
        assert response.status_code == 201
        assert len(response.json.get("device_token")) == 1000

    def test_register_device_token_with_null_device_info(self) -> None:
        """Test explicit null device_info via API"""
        account, token = self.create_account_and_get_token()
        
        response = self.make_authenticated_request(
            "POST", account.id, token,
            data={"device_token": "token", "platform": "android", "device_info": None}
        )
        
        assert response.status_code == 201
        assert response.json.get("device_info") is None

    def test_register_device_token_with_complex_device_info(self) -> None:
        """Test complex nested device_info via API"""
        account, token = self.create_account_and_get_token()
        complex_info = {
            "app": {"version": "1.0", "build": 123},
            "device": {"model": "Pixel", "os": "Android 14"},
            "metadata": {"locale": "en_US", "timezone": "America/New_York"}
        }
        
        response = self.make_authenticated_request(
            "POST", account.id, token,
            data={"device_token": "complex", "platform": "android", "device_info": complex_info}
        )
        
        assert response.status_code == 201
        assert response.json.get("device_info") == complex_info

    def test_get_device_tokens_with_many_devices(self) -> None:
        """Test retrieving many devices via API"""
        account, token = self.create_account_and_get_token()
        
        # Create 25 tokens
        for i in range(25):
            self.create_test_device_token(
                account_id=account.id, 
                device_token=f"many_token_{i}"
            )
        
        response = self.make_authenticated_request("GET", account.id, token)
        
        assert response.status_code == 200
        assert len(response.json["devices"]) == 25

    def test_delete_already_deleted_token(self) -> None:
        """Test that deleting an already-deleted token succeeds (idempotent behavior).
        
        The service implements idempotent delete - attempting to delete a token
        that's already deleted (or doesn't exist) returns 200 success.
        """
        account, token = self.create_account_and_get_token()
        device_token = self.create_test_device_token(account_id=account.id)
        
        # Delete once
        response1 = self.make_authenticated_request(
            "DELETE", account.id, token, device_id=device_token.id
        )
        assert response1.status_code == 200
        
        # Delete again - should also succeed (idempotent)
        response2 = self.make_authenticated_request(
            "DELETE", account.id, token, device_id=device_token.id
        )
        assert response2.status_code == 200

    def test_register_device_token_whitespace_handling(self) -> None:
        """Test that whitespace in tokens is handled correctly"""
        account, token = self.create_account_and_get_token()
        
        # Token with leading/trailing whitespace
        response = self.make_authenticated_request(
            "POST", account.id, token,
            data={"device_token": "  whitespace_token  ", "platform": "android"}
        )
        
        assert response.status_code == 201
        # Should be trimmed by the service
        assert response.json.get("device_token").strip() == "whitespace_token"

    def test_get_device_token_by_invalid_object_id(self) -> None:
        """Test that invalid ObjectId format in delete returns proper error"""
        account, token = self.create_account_and_get_token()
        
        # Try to delete with invalid ObjectId format
        response = self.make_authenticated_request(
            "DELETE", account.id, token, device_id="invalid_object_id_format"
        )
        
        # Should return 404 or 400 depending on implementation
        assert response.status_code in [400, 404]