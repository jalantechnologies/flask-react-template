from datetime import datetime, timedelta

from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.errors import (
    DeviceTokenNotFoundError,
    InvalidPlatformError
)
from modules.device_token.types import DeviceTokenErrorCode
from tests.modules.device_token.base_test_device_token import BaseTestDeviceToken


class TestDeviceTokenService(BaseTestDeviceToken):
    def setUp(self) -> None:
        super().setUp()
        self.account = self.create_test_account()

    def test_register_device_token_success(self) -> None:
        device_token = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token="fcm_token_123",
            platform="android",
            device_info={"app_version": "1.0.0"},
        )

        assert device_token.account_id == self.account.id
        assert device_token.device_token == "fcm_token_123"
        assert device_token.platform == "android"
        assert device_token.device_info == {"app_version": "1.0.0"}
        assert device_token.active is True
        assert device_token.id is not None

    def test_register_device_token_without_device_info(self) -> None:
        device_token = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token="fcm_token_456",
            platform="ios",
        )

        assert device_token.account_id == self.account.id
        assert device_token.device_token == "fcm_token_456"
        assert device_token.platform == "ios"
        assert device_token.device_info is None
        assert device_token.active is True

    def test_register_device_token_all_platforms(self) -> None:
        for platform in ["android", "ios"]:
            device_token = DeviceTokenService.register_device_token(
                account_id=self.account.id,
                device_token=f"{platform}_token",
                platform=platform,
            )
            assert device_token.platform == platform

    def test_register_device_token_invalid_platform(self) -> None:
        try:
            DeviceTokenService.register_device_token(
                account_id=self.account.id,
                device_token="token",
                platform="windows_phone",
            )
            assert False, "Expected InvalidPlatformError"
        except InvalidPlatformError as exc:
            assert exc.code == DeviceTokenErrorCode.INVALID_PLATFORM

    def test_register_device_token_upsert_behavior(self) -> None:
        token1 = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token="same_token",
            platform="android",
            device_info={"app_version": "1.0"},
        )

        token2 = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token="same_token",
            platform="android",
            device_info={"app_version": "2.0"},
        )

        assert token1.id == token2.id
        assert token2.device_info == {"app_version": "2.0"}

    def test_get_device_tokens_for_account_empty(self) -> None:
        tokens = DeviceTokenService.get_device_tokens_for_account(account_id=self.account.id)
        assert len(tokens) == 0

    def test_get_device_tokens_for_account_with_tokens(self) -> None:
        created_tokens = self.create_multiple_test_tokens(account_id=self.account.id, count=3)

        tokens = DeviceTokenService.get_device_tokens_for_account(account_id=self.account.id)

        token_ids = [t.id for t in tokens]
        for created_token in created_tokens:
            assert created_token.id in token_ids

    def test_get_device_tokens_excludes_inactive(self) -> None:
        active_token = self.create_test_device_token(
            account_id=self.account.id, device_token="active_token"
        )
        inactive_token = self.create_test_device_token(
            account_id=self.account.id, device_token="inactive_token"
        )

        DeviceTokenService.unregister_device_token(
            account_id=self.account.id, device_token_id=inactive_token.id
        )

        tokens = DeviceTokenService.get_device_tokens_for_account(account_id=self.account.id)

        assert len(tokens) == 1
        assert tokens[0].id == active_token.id

    def test_unregister_device_token_success(self) -> None:
        device_token = self.create_test_device_token(account_id=self.account.id)

        DeviceTokenService.unregister_device_token(
            account_id=self.account.id, device_token_id=device_token.id
        )

        tokens = DeviceTokenService.get_device_tokens_for_account(account_id=self.account.id)
        assert len(tokens) == 0

    def test_unregister_device_token_not_found(self) -> None:
        try:
            DeviceTokenService.unregister_device_token(
                account_id=self.account.id, device_token_id="nonexistent_id"
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError as exc:
            assert exc.code == DeviceTokenErrorCode.NOT_FOUND

    def test_unregister_device_token_wrong_account(self) -> None:
        """Test that attempting to unregister a token from a different account succeeds silently.
        
        The service implements idempotent delete with account filtering:
        - When unregistering with account_id that doesn't match the token's owner,
          the service filters by account_id, finds nothing, and succeeds with no effect
        - This is safe because authentication layer prevents unauthorized access
        - The original token remains untouched
        """
        other_account = self.create_test_account(username="other@example.com")
        device_token = self.create_test_device_token(account_id=other_account.id)

        # Attempt to unregister using wrong account_id - succeeds silently
        result = DeviceTokenService.unregister_device_token(
            account_id=self.account.id, device_token_id=device_token.id
        )
        
        # Should succeed (idempotent behavior)
        assert result.success is True
        
        # Verify the token still exists for the original owner
        tokens = DeviceTokenService.get_device_tokens_for_account(account_id=other_account.id)
        assert len(tokens) == 1
        assert tokens[0].id == device_token.id

    def test_mark_token_as_invalid(self) -> None:
        account2 = self.create_test_account(username="user2@example.com")
        token_string = "invalid_fcm_token"

        token1 = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token=token_string,
            platform="android",
        )
        token2 = DeviceTokenService.register_device_token(
            account_id=account2.id,
            device_token=token_string,
            platform="android",
        )

        DeviceTokenService.mark_token_as_invalid(token=token_string)

        account1_tokens = DeviceTokenService.get_device_tokens_for_account(account_id=self.account.id)
        account2_tokens = DeviceTokenService.get_device_tokens_for_account(account_id=account2.id)

        assert len(account1_tokens) == 0
        assert len(account2_tokens) == 0

    def test_cleanup_inactive_tokens(self) -> None:
        cutoff = datetime.now() - timedelta(days=30)

        recent = self.insert_raw_device_token(
            account_id=self.account.id,
            device_token="recent",
            platform="android",
            last_used_at=datetime.now(),
        )

        old = self.insert_raw_device_token(
            account_id=self.account.id,
            device_token="old",
            platform="ios",
            last_used_at=cutoff - timedelta(days=1),
        )

        cleaned_count = DeviceTokenService.cleanup_inactive_tokens(days_old=30)

        assert cleaned_count == 1

        tokens = DeviceTokenService.get_device_tokens_for_account(
            account_id=self.account.id
        )

        assert len(tokens) == 1
        assert tokens[0].device_token == "recent"


    def test_cross_account_isolation(self) -> None:
        account2 = self.create_test_account(username="user2@example.com")

        self.insert_raw_device_token(
            account_id=self.account.id,
            device_token="token_a",
            platform="android",
        )

        self.insert_raw_device_token(
            account_id=account2.id,
            device_token="token_b",
            platform="ios",
        )

        account1_tokens = DeviceTokenService.get_device_tokens_for_account(
            account_id=self.account.id
        )
        account2_tokens = DeviceTokenService.get_device_tokens_for_account(
            account_id=account2.id
        )

        assert len(account1_tokens) == 1
        assert account1_tokens[0].device_token == "token_a"

        assert len(account2_tokens) == 1
        assert account2_tokens[0].device_token == "token_b"

    def test_register_device_token_with_special_characters(self) -> None:
        """Test device tokens with special characters"""
        device_token = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token="token_with_special!@#$%^&*()",
            platform="android",
        )
        
        assert device_token.device_token == "token_with_special!@#$%^&*()"
        assert device_token.active is True

    def test_register_device_token_with_very_long_token(self) -> None:
        """Test handling of extremely long device tokens"""
        very_long_token = "x" * 1000
        
        device_token = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token=very_long_token,
            platform="android",
        )
        
        assert len(device_token.device_token) == 1000
        assert device_token.active is True

    def test_device_info_preserves_nested_objects(self) -> None:
        """Test that complex device_info structures are preserved"""
        complex_info = {
            "app": {"version": "1.0", "build": 123},
            "device": {"model": "Pixel", "os": "Android 14"},
            "metadata": {"locale": "en_US", "timezone": "America/New_York"}
        }
        
        device_token = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token="complex_token",
            platform="android",
            device_info=complex_info,
        )
        
        assert device_token.device_info == complex_info

    def test_cleanup_with_no_old_tokens(self) -> None:
        """Test cleanup when there are no old tokens to clean"""
        # Create only recent tokens
        self.create_test_device_token(
            account_id=self.account.id,
            device_token="recent_token",
        )
        
        cleaned_count = DeviceTokenService.cleanup_inactive_tokens(days_old=30)
        
        assert cleaned_count == 0
        
        # Verify token still exists
        tokens = DeviceTokenService.get_device_tokens_for_account(
            account_id=self.account.id
        )
        assert len(tokens) == 1

    def test_get_device_tokens_with_many_devices(self) -> None:
        """Test behavior when account has many devices"""
        # Create 25 tokens
        for i in range(25):
            DeviceTokenService.register_device_token(
                account_id=self.account.id,
                device_token=f"token_{i}",
                platform="android",
            )
        
        tokens = DeviceTokenService.get_device_tokens_for_account(
            account_id=self.account.id
        )
        
        assert len(tokens) == 25

    def test_register_device_token_with_explicit_none_device_info(self) -> None:
        """Test explicit None vs missing device_info"""
        device_token = DeviceTokenService.register_device_token(
            account_id=self.account.id,
            device_token="token_none",
            platform="ios",
            device_info=None,
        )
        
        assert device_token.device_info is None

    def test_unregister_device_token_idempotency(self) -> None:
        """Test that unregistering twice succeeds (idempotent behavior).
        
        The service implements idempotent delete - attempting to delete a token
        that's already deleted returns success with no error.
        """
        device_token = self.create_test_device_token(account_id=self.account.id)
        
        # First unregister - should succeed
        result1 = DeviceTokenService.unregister_device_token(
            account_id=self.account.id, device_token_id=device_token.id
        )
        assert result1.success is True
        
        # Verify it's deleted
        tokens = DeviceTokenService.get_device_tokens_for_account(account_id=self.account.id)
        assert len(tokens) == 0
        
        # Second unregister - should also succeed (idempotent)
        result2 = DeviceTokenService.unregister_device_token(
            account_id=self.account.id, device_token_id=device_token.id
        )
        assert result2.success is True

    def test_get_device_tokens_includes_inactive_when_not_filtered(self) -> None:
        """Test that inactive tokens are included when active_only=False"""
        from modules.device_token.internal.device_token_reader import DeviceTokenReader
        from modules.device_token.types import GetDeviceTokensParams
        
        # Create active and inactive tokens
        active = self.create_test_device_token(
            account_id=self.account.id, device_token="active"
        )
        inactive = self.create_test_device_token(
            account_id=self.account.id, device_token="inactive"
        )
        
        # Mark one as inactive
        DeviceTokenService.unregister_device_token(
            account_id=self.account.id, device_token_id=inactive.id
        )
        
        # Get with active_only=False (should include inactive)
        params = GetDeviceTokensParams(account_id=self.account.id, active_only=False)
        all_tokens = DeviceTokenReader.get_device_tokens_by_account_id(params=params)
        
        assert len(all_tokens) == 2  # Both active and inactive
        
        # Get with active_only=True (default behavior)
        params_active = GetDeviceTokensParams(account_id=self.account.id, active_only=True)
        active_tokens = DeviceTokenReader.get_device_tokens_by_account_id(params=params_active)
        
        assert len(active_tokens) == 1  # Only active
        assert active_tokens[0].device_token == "active"

    def test_get_device_token_by_token_string(self) -> None:
        """Test retrieving device token by its token string"""
        from modules.device_token.internal.device_token_reader import DeviceTokenReader
        
        # Create a device token
        created = self.create_test_device_token(
            account_id=self.account.id,
            device_token="unique_token_string_12345"
        )
        
        # Find by token string
        found = DeviceTokenReader.get_device_token_by_token(token="unique_token_string_12345")
        
        assert found is not None
        assert found.id == created.id
        assert found.device_token == "unique_token_string_12345"

    def test_get_device_token_by_nonexistent_token_string(self) -> None:
        """Test that getting by non-existent token returns None"""
        from modules.device_token.internal.device_token_reader import DeviceTokenReader
        
        found = DeviceTokenReader.get_device_token_by_token(token="nonexistent_token_999")
        
        assert found is None

    def test_get_device_token_by_inactive_token_string(self) -> None:
        """Test that getting inactive token by string returns None"""
        from modules.device_token.internal.device_token_reader import DeviceTokenReader
        
        # Create and then deactivate a token
        created = self.create_test_device_token(
            account_id=self.account.id,
            device_token="will_be_inactive"
        )
        
        DeviceTokenService.unregister_device_token(
            account_id=self.account.id,
            device_token_id=created.id
        )
        
        # Try to find by token string - should return None since it's inactive
        found = DeviceTokenReader.get_device_token_by_token(token="will_be_inactive")
        
        assert found is None

    def test_get_device_token_by_id_with_params(self) -> None:
        """Test getting device token by ID using params object"""
        from modules.device_token.internal.device_token_reader import DeviceTokenReader
        from modules.device_token.types import GetDeviceTokenParams
        
        # Create a token
        created = self.create_test_device_token(account_id=self.account.id)
        
        # Get by ID using params
        params = GetDeviceTokenParams(device_token_id=created.id)
        found = DeviceTokenReader.get_device_token_by_id(params=params)
        
        assert found is not None
        assert found.id == created.id
        assert found.device_token == created.device_token

    def test_get_device_token_by_id_inactive_not_found(self) -> None:
        """Test that getting inactive token by ID raises error"""
        from modules.device_token.internal.device_token_reader import DeviceTokenReader
        from modules.device_token.types import GetDeviceTokenParams
        
        # Create and deactivate
        created = self.create_test_device_token(account_id=self.account.id)
        DeviceTokenService.unregister_device_token(
            account_id=self.account.id,
            device_token_id=created.id
        )
        
        # Try to get inactive token by ID - should raise error
        try:
            params = GetDeviceTokenParams(device_token_id=created.id)
            DeviceTokenReader.get_device_token_by_id(params=params)
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError:
            pass  # Expected

    def test_device_tokens_sorted_by_created_at(self) -> None:
        """Test that device tokens are returned sorted by created_at descending"""
        from modules.device_token.internal.device_token_reader import DeviceTokenReader
        from modules.device_token.types import GetDeviceTokensParams
        import time
        
        # Create tokens with slight time delays
        token1 = self.create_test_device_token(
            account_id=self.account.id, device_token="first"
        )
        time.sleep(0.01)
        
        token2 = self.create_test_device_token(
            account_id=self.account.id, device_token="second"
        )
        time.sleep(0.01)
        
        token3 = self.create_test_device_token(
            account_id=self.account.id, device_token="third"
        )
        
        # Get all tokens
        params = GetDeviceTokensParams(account_id=self.account.id, active_only=True)
        tokens = DeviceTokenReader.get_device_tokens_by_account_id(params=params)
        
        # Should be in reverse chronological order (newest first)
        assert tokens[0].device_token == "third"
        assert tokens[1].device_token == "second"
        assert tokens[2].device_token == "first"