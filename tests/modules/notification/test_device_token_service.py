import uuid

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams
from tests.modules.notification.base_test_notification import BaseTestNotification


class TestDeviceTokenService(BaseTestNotification):
    def _create_test_account(self, username_suffix=""):

        unique_id = str(uuid.uuid4())[:8]
        username = f"testuser{username_suffix}_{unique_id}@example.com"

        return AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password", username=username
            )
        )

    def test_upsert_device_token_create_new(self) -> None:
        """Test creating a new device token"""
        account = self._create_test_account()

        params = RegisterDeviceTokenParams(user_id=account.id, token="fcm_token_123", device_type="android")

        device_token = NotificationService.upsert_device_token(params=params)

        assert device_token.token == "fcm_token_123"
        assert device_token.user_id == account.id
        assert device_token.device_type == "android"
        assert device_token.id is not None
        assert device_token.created_at is not None
        assert device_token.updated_at is not None

    def test_upsert_device_token_update_existing(self) -> None:
        """Test updating an existing device token"""
        account1 = self._create_test_account("_1")
        account2 = self._create_test_account("_2")

        # Create initial token for account1
        params1 = RegisterDeviceTokenParams(user_id=account1.id, token="fcm_token_123", device_type="android")
        device_token1 = NotificationService.upsert_device_token(params=params1)

        # Update same token for account2
        params2 = RegisterDeviceTokenParams(
            user_id=account2.id, token="fcm_token_123", device_type="ios"  # Same token  # Different device type
        )
        device_token2 = NotificationService.upsert_device_token(params=params2)

        # Should be the same record (same ID) but updated
        assert device_token2.id == device_token1.id
        assert device_token2.token == "fcm_token_123"
        assert device_token2.user_id == account2.id  # Updated to account2
        assert device_token2.device_type == "ios"  # Updated device type
        assert device_token2.updated_at >= device_token1.created_at

    def test_get_user_fcm_tokens_multiple_tokens(self) -> None:
        """Test getting multiple tokens for a user"""
        account = self._create_test_account()

        # Create multiple tokens for the same user
        tokens_to_create = [("fcm_token_1", "android"), ("fcm_token_2", "ios"), ("fcm_token_3", "web")]

        for token, device_type in tokens_to_create:
            NotificationService.upsert_device_token(
                params=RegisterDeviceTokenParams(user_id=account.id, token=token, device_type=device_type)
            )

        user_tokens = NotificationService.get_user_fcm_tokens(account.id)

        assert len(user_tokens) == 3
        assert "fcm_token_1" in user_tokens
        assert "fcm_token_2" in user_tokens
        assert "fcm_token_3" in user_tokens

    def test_get_user_fcm_tokens_no_tokens(self) -> None:
        """Test getting tokens for user with no tokens"""
        account = self._create_test_account()

        user_tokens = NotificationService.get_user_fcm_tokens(account.id)

        assert user_tokens == []

    def test_get_user_fcm_tokens_different_users(self) -> None:
        """Test that tokens are properly isolated between users"""
        account1 = self._create_test_account("_1")
        account2 = self._create_test_account("_2")

        # Create tokens for each user
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account1.id, token="fcm_token_user1", device_type="android")
        )

        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account2.id, token="fcm_token_user2", device_type="ios")
        )

        user1_tokens = NotificationService.get_user_fcm_tokens(account1.id)
        user2_tokens = NotificationService.get_user_fcm_tokens(account2.id)

        assert len(user1_tokens) == 1
        assert len(user2_tokens) == 1
        assert "fcm_token_user1" in user1_tokens
        assert "fcm_token_user2" in user2_tokens
        assert "fcm_token_user1" not in user2_tokens
        assert "fcm_token_user2" not in user1_tokens

    def test_remove_device_token_success(self) -> None:
        """Test successfully removing a device token"""
        account = self._create_test_account()

        # Create a token
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm_token_to_remove", device_type="android")
        )

        # Verify token exists
        user_tokens_before = NotificationService.get_user_fcm_tokens(account.id)
        assert "fcm_token_to_remove" in user_tokens_before

        # Remove the token
        result = NotificationService.remove_device_token("fcm_token_to_remove")

        assert result is True

        # Verify token is removed
        user_tokens_after = NotificationService.get_user_fcm_tokens(account.id)
        assert "fcm_token_to_remove" not in user_tokens_after

    def test_remove_device_token_not_found(self) -> None:
        """Test removing a non-existent device token"""
        result = NotificationService.remove_device_token("non_existent_token")

        assert result is False

    def test_remove_device_token_doesnt_affect_other_tokens(self) -> None:
        """Test that removing one token doesn't affect other tokens"""
        account = self._create_test_account()

        # Create multiple tokens
        tokens_to_create = ["fcm_token_1", "fcm_token_2", "fcm_token_3"]
        for token in tokens_to_create:
            NotificationService.upsert_device_token(
                params=RegisterDeviceTokenParams(user_id=account.id, token=token, device_type="android")
            )

        # Remove one token
        result = NotificationService.remove_device_token("fcm_token_2")
        assert result is True

        # Verify other tokens still exist
        user_tokens = NotificationService.get_user_fcm_tokens(account.id)
        assert len(user_tokens) == 2
        assert "fcm_token_1" in user_tokens
        assert "fcm_token_3" in user_tokens
        assert "fcm_token_2" not in user_tokens

    def test_get_user_fcm_tokens_nonexistent_user(self) -> None:
        """Test getting tokens for a non-existent user"""
        fake_user_id = "661e42ec98423703a299a899"

        user_tokens = NotificationService.get_user_fcm_tokens(fake_user_id)

        assert user_tokens == []

    def test_upsert_device_token_same_user_multiple_devices(self) -> None:
        """Test that a user can have multiple tokens for different devices"""
        account = self._create_test_account()

        # Create tokens for different device types
        android_token = NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm_token_android", device_type="android")
        )

        ios_token = NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm_token_ios", device_type="ios")
        )

        web_token = NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm_token_web", device_type="web")
        )

        # All should be different records
        assert android_token.id != ios_token.id
        assert android_token.id != web_token.id
        assert ios_token.id != web_token.id

        # All should belong to the same user
        assert android_token.user_id == account.id
        assert ios_token.user_id == account.id
        assert web_token.user_id == account.id

        # User should have all tokens
        user_tokens = NotificationService.get_user_fcm_tokens(account.id)
        assert len(user_tokens) == 3
        assert "fcm_token_android" in user_tokens
        assert "fcm_token_ios" in user_tokens
        assert "fcm_token_web" in user_tokens
