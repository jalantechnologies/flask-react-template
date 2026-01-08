from modules.authentication.types import AccessTokenErrorCode
from modules.device_token.types import DeviceTokenErrorCode
from tests.modules.device_token.base_test_device_token import BaseTestDeviceToken


class TestDeviceTokenApi(BaseTestDeviceToken):

    def test_post_success(self):
        """Test successful device token registration"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={
                "device_token": "new_token_123",
                "platform": "android",
                "device_info": {"app_version": "1.0.0"}
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["device_token"], "new_token_123")
        self.assertEqual(data["platform"], "android")
        self.assertTrue(data["active"])

    def test_post_ios_platform(self):
        """Test registration with iOS platform"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "ios_token", "platform": "ios"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["platform"], "ios")

    def test_post_empty_body(self):
        """Test POST with empty request body"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request("POST", account.id, token, data={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["code"], DeviceTokenErrorCode.BAD_REQUEST)

    def test_post_missing_device_token(self):
        """Test POST without device_token field"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"platform": "android"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Device token is required", data["message"])

    def test_post_empty_device_token(self):
        """Test POST with empty device_token string"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "   ", "platform": "android"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Device token is required", data["message"])

    def test_post_missing_platform(self):
        """Test POST without platform field"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token_123"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Platform is required", data["message"])

    def test_post_empty_platform(self):
        """Test POST with empty platform string"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token_123", "platform": "  "},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Platform is required", data["message"])

    def test_post_invalid_platform(self):
        """Test POST with unsupported platform value"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token_123", "platform": "windows"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["code"], DeviceTokenErrorCode.INVALID_PLATFORM)

    def test_post_invalid_device_info(self):
        """Test POST with non-dict device_info"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "x", "platform": "android", "device_info": "bad"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Device info must be an object", data["message"])

    def test_post_duplicate_token_same_account(self):
        """Test registering same token twice for same account"""
        account, token = self.create_account_and_get_token()
        self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "dup_token", "platform": "android"},
        )
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "dup_token", "platform": "android"},
        )
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertEqual(data["code"], DeviceTokenErrorCode.CONFLICT)

    def test_post_duplicate_token_different_account(self):
        """Test registering same token for different accounts"""
        account1, token1 = self.create_account_and_get_token("user1@example.com")
        account2, token2 = self.create_account_and_get_token("user2@example.com")
        
        self.make_authenticated_request(
            "POST",
            account1.id,
            token1,
            data={"device_token": "shared_token", "platform": "android"},
        )
        response = self.make_authenticated_request(
            "POST",
            account2.id,
            token2,
            data={"device_token": "shared_token", "platform": "android"},
        )
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertIn("already registered to another account", data["message"])

    def test_post_no_auth(self):
        """Test POST without authentication"""
        account, _ = self.create_account_and_get_token()
        response = self.make_unauthenticated_request(
            "POST",
            account.id,
            data={"device_token": "token", "platform": "android"}
        )
        self.assertEqual(response.status_code, 401)

    def test_post_platform_case_insensitive(self):
        """Test that platform values are case-insensitive"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "case_token", "platform": "ANDROID"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["platform"], "android")

    def test_get_success(self):
        """Test GET with devices registered"""
        account, token = self.create_account_and_get_token()
        self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token1", "platform": "android"},
        )
        self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token2", "platform": "ios"},
        )

        response = self.make_authenticated_request("GET", account.id, token)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["devices"]), 2)

    def test_get_empty_list(self):
        """Test GET with no devices registered"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request("GET", account.id, token)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["devices"], [])

    def test_get_no_auth(self):
        """Test GET without authentication"""
        account, _ = self.create_account_and_get_token()
        response = self.make_unauthenticated_request("GET", account.id)
        self.assertEqual(response.status_code, 401)

    def test_patch_update_device_token(self):
        account, token = self.create_account_and_get_token()

        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "old_token", "platform": "android"},
        )
        device_id = created.get_json()["id"]

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=device_id,
            data={"device_token": "new_token"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["id"], device_id)
        self.assertEqual(data["platform"], "android")
        self.assertTrue(data["active"])
        self.assertIsNotNone(data["last_used_at"])

    def test_patch_update_device_info(self):
        account, token = self.create_account_and_get_token()

        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "patch_me", "platform": "android"},
        )
        device_id = created.get_json()["id"]

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=device_id,
            data={"device_info": {"os": "android", "version": "14"}},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["id"], device_id)
        self.assertEqual(data["platform"], "android")
        self.assertEqual(data["device_info"]["os"], "android")
        self.assertEqual(data["device_info"]["version"], "14")
        self.assertTrue(data["active"])
        self.assertIsNotNone(data["last_used_at"])

    def test_patch_update_both_fields(self):
        account, token = self.create_account_and_get_token()

        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "old", "platform": "android"},
        )
        device_id = created.get_json()["id"]

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=device_id,
            data={"device_token": "new", "device_info": {"updated": True}},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["id"], device_id)
        self.assertEqual(data["platform"], "android")
        self.assertTrue(data["device_info"]["updated"])
        self.assertTrue(data["active"])
        self.assertIsNotNone(data["last_used_at"])

    def test_patch_heartbeat(self):
        """Test PATCH with empty body (heartbeat)"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "heartbeat", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=created.get_json()["id"],
            data={},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data["last_used_at"])

    def test_patch_empty_device_token(self):
        """Test PATCH with empty device_token string"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "valid_token", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=created.get_json()["id"],
            data={"device_token": "   "},
        )

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Device token cannot be empty", data["message"])

    def test_patch_invalid_device_info(self):
        """Test PATCH with non-dict device_info"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=created.get_json()["id"],
            data={"device_info": "not_a_dict"},
        )

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Device info must be an object", data["message"])

    def test_patch_invalid_field(self):
        """Test PATCH with unsupported field"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "bad_patch", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=created.get_json()["id"],
            data={"active": False},
        )

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Unsupported fields", data["message"])

    def test_patch_multiple_invalid_fields(self):
        """Test PATCH with multiple unsupported fields"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=created.get_json()["id"],
            data={"active": False, "platform": "ios"},
        )

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Unsupported fields", data["message"])

    def test_patch_not_found(self):
        """Test PATCH with non-existent device ID"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id="507f1f77bcf86cd799439011",
            data={"device_info": {"x": 1}},
        )
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data["code"], DeviceTokenErrorCode.NOT_FOUND)

    def test_patch_wrong_account(self):
        """Test PATCH with device belonging to different account"""
        account1, token1 = self.create_account_and_get_token("user1@example.com")
        account2, token2 = self.create_account_and_get_token("user2@example.com")
        
        created = self.make_authenticated_request(
            "POST",
            account1.id,
            token1,
            data={"device_token": "account1_token", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "PATCH",
            account2.id,
            token2,
            device_id=created.get_json()["id"],
            data={"device_info": {"hacked": True}},
        )

        self.assertEqual(response.status_code, 404)

    def test_patch_no_auth(self):
        """Test PATCH without authentication"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token", "platform": "android"},
        )

        response = self.make_unauthenticated_request(
            "PATCH",
            account.id,
            device_id=created.get_json()["id"],
            data={"device_info": {"x": 1}}
        )
        self.assertEqual(response.status_code, 401)

    def test_patch_duplicate_device_token(self):
        """Test PATCH to device_token that already exists"""
        account, token = self.create_account_and_get_token()
        self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "existing_token", "platform": "android"},
        )
        created2 = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "new_token", "platform": "ios"},
        )

        response = self.make_authenticated_request(
            "PATCH",
            account.id,
            token,
            device_id=created2.get_json()["id"],
            data={"device_token": "existing_token"},
        )

        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertEqual(data["code"], DeviceTokenErrorCode.CONFLICT)

    def test_delete_success(self):
        """Test successful device deletion"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "delete_me", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "DELETE",
            account.id,
            token,
            device_id=created.get_json()["id"],
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")

    def test_delete_not_found(self):
        """Test DELETE with non-existent device ID"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "DELETE",
            account.id,
            token,
            device_id="507f1f77bcf86cd799439011",
        )
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data["code"], DeviceTokenErrorCode.NOT_FOUND)

    def test_delete_invalid_object_id(self):
        """Test DELETE with invalid ObjectId format"""
        account, token = self.create_account_and_get_token()
        response = self.make_authenticated_request(
            "DELETE",
            account.id,
            token,
            device_id="not_an_object_id",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_wrong_account(self):
        """Test DELETE with device belonging to different account"""
        account1, token1 = self.create_account_and_get_token("user1@example.com")
        account2, token2 = self.create_account_and_get_token("user2@example.com")
        
        created = self.make_authenticated_request(
            "POST",
            account1.id,
            token1,
            data={"device_token": "account1_token", "platform": "android"},
        )

        response = self.make_authenticated_request(
            "DELETE",
            account2.id,
            token2,
            device_id=created.get_json()["id"],
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_already_deleted(self):
        """Test DELETE on already deleted device"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "delete_twice", "platform": "android"},
        )

        device_id = created.get_json()["id"]
        
        self.make_authenticated_request(
            "DELETE",
            account.id,
            token,
            device_id=device_id,
        )

        response = self.make_authenticated_request(
            "DELETE",
            account.id,
            token,
            device_id=device_id,
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_no_auth(self):
        """Test DELETE without authentication"""
        account, token = self.create_account_and_get_token()
        created = self.make_authenticated_request(
            "POST",
            account.id,
            token,
            data={"device_token": "token", "platform": "android"},
        )

        response = self.make_unauthenticated_request(
            "DELETE",
            account.id,
            device_id=created.get_json()["id"]
        )
        self.assertEqual(response.status_code, 401)