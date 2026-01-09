from modules.device_token.device_token_service import DeviceTokenService
from modules.device_token.errors import (
    DeviceTokenNotFoundError,
    DeviceTokenConflictError,
)
from modules.device_token.types import (
    Platform,
    CreateDeviceTokenParams,
    DeviceTokenErrorCode,
    DeleteDeviceTokenParams,
    GetDeviceTokensParams,
    UpdateDeviceTokenParams
)
from tests.modules.device_token.base_test_device_token import BaseTestDeviceToken


class TestDeviceTokenService(BaseTestDeviceToken):
    def setUp(self) -> None:
        super().setUp()
        self.account = self.create_test_account()

    def test_create_device_token_success(self):
        """Test successful device token creation"""
        params = CreateDeviceTokenParams(
            account_id=self.account.id,
            device_token="token_1",
            platform=Platform.ANDROID,
        )

        token = DeviceTokenService.create_device_token(params=params)

        assert token.device_token == "token_1"
        assert token.platform == Platform.ANDROID
        assert token.active is True
        assert token.account_id == self.account.id
        assert token.id is not None
        assert token.created_at is not None
        assert token.updated_at is not None
        assert token.last_used_at is not None

    def test_create_device_token_with_device_info(self):
        """Test creating device token with device_info"""
        params = CreateDeviceTokenParams(
            account_id=self.account.id,
            device_token="token_with_info",
            platform=Platform.IOS,
            device_info={"model": "iPhone 13", "os_version": "15.0"},
        )

        token = DeviceTokenService.create_device_token(params=params)

        assert token.device_info is not None
        assert token.device_info["model"] == "iPhone 13"
        assert token.device_info["os_version"] == "15.0"
        assert token.platform == Platform.IOS

    def test_create_device_token_without_device_info(self):
        """Test creating device token without device_info"""
        params = CreateDeviceTokenParams(
            account_id=self.account.id,
            device_token="token_no_info",
            platform=Platform.ANDROID,
            device_info=None,
        )

        token = DeviceTokenService.create_device_token(params=params)

        assert token.device_info is None

    def test_create_duplicate_token_conflict(self):
        """Test creating duplicate token for same account raises conflict"""
        params = CreateDeviceTokenParams(
            account_id=self.account.id,
            device_token="dup_token",
            platform=Platform.ANDROID,
        )

        DeviceTokenService.create_device_token(params=params)

        try:
            DeviceTokenService.create_device_token(params=params)
            assert False, "Expected DeviceTokenConflictError"
        except DeviceTokenConflictError as exc:
            assert exc.code == DeviceTokenErrorCode.CONFLICT
            assert "already registered" in exc.message

    def test_create_duplicate_token_different_account_conflict(self):
        """Test creating same token for different accounts raises conflict"""
        other_account = self.create_test_account("other@example.com")

        DeviceTokenService.create_device_token(
            params=CreateDeviceTokenParams(
                account_id=self.account.id,
                device_token="shared_token",
                platform=Platform.ANDROID,
            )
        )

        try:
            DeviceTokenService.create_device_token(
                params=CreateDeviceTokenParams(
                    account_id=other_account.id,
                    device_token="shared_token",
                    platform=Platform.ANDROID,
                )
            )
            assert False, "Expected DeviceTokenConflictError"
        except DeviceTokenConflictError as exc:
            assert exc.code == DeviceTokenErrorCode.CONFLICT
            assert "another account" in exc.message

    def test_create_android_platform(self):
        """Test creating token with Android platform"""
        params = CreateDeviceTokenParams(
            account_id=self.account.id,
            device_token="android_token",
            platform=Platform.ANDROID,
        )

        token = DeviceTokenService.create_device_token(params=params)
        assert token.platform == Platform.ANDROID

    def test_create_ios_platform(self):
        """Test creating token with iOS platform"""
        params = CreateDeviceTokenParams(
            account_id=self.account.id,
            device_token="ios_token",
            platform=Platform.IOS,
        )

        token = DeviceTokenService.create_device_token(params=params)
        assert token.platform == Platform.IOS

    def test_get_device_tokens_for_account_empty(self):
        """Test getting device tokens when none exist"""
        params = GetDeviceTokensParams(account_id=self.account.id)
        
        tokens = DeviceTokenService.get_device_tokens_for_account(params=params)
        
        assert tokens == []

    def test_get_device_tokens_for_account_single(self):
        """Test getting device tokens with single device"""
        self.create_test_device_token(self.account.id, "token_1")
        
        params = GetDeviceTokensParams(account_id=self.account.id)
        tokens = DeviceTokenService.get_device_tokens_for_account(params=params)
        
        assert len(tokens) == 1
        assert tokens[0].device_token == "token_1"

    def test_get_device_tokens_for_account_multiple(self):
        """Test getting device tokens with multiple devices"""
        self.create_test_device_token(self.account.id, "token_1")
        self.create_test_device_token(self.account.id, "token_2")
        self.create_test_device_token(self.account.id, "token_3")
        
        params = GetDeviceTokensParams(account_id=self.account.id)
        tokens = DeviceTokenService.get_device_tokens_for_account(params=params)
        
        assert len(tokens) == 3

    def test_get_device_tokens_sorted_by_created_at(self):
        """Test that device tokens are returned sorted by creation date (newest first)"""
        token1 = self.create_test_device_token(self.account.id, "old_token")
        token2 = self.create_test_device_token(self.account.id, "new_token")
        
        params = GetDeviceTokensParams(account_id=self.account.id)
        tokens = DeviceTokenService.get_device_tokens_for_account(params=params)
        
        assert tokens[0].device_token == "new_token"
        assert tokens[1].device_token == "old_token"

    def test_get_device_tokens_only_active(self):
        """Test that only active devices are returned"""
        token = self.create_test_device_token(self.account.id, "active_token")
        inactive_token = self.create_test_device_token(self.account.id, "inactive_token")
        
        DeviceTokenService.deactivate_device_token(
            params=DeleteDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=inactive_token.id,
            )
        )
        
        params = GetDeviceTokensParams(account_id=self.account.id)
        tokens = DeviceTokenService.get_device_tokens_for_account(params=params)
        
        assert len(tokens) == 1
        assert tokens[0].device_token == "active_token"

    def test_get_device_tokens_different_accounts(self):
        """Test that devices are scoped to the correct account"""
        other_account = self.create_test_account("other@example.com")
        
        self.create_test_device_token(self.account.id, "account1_token")
        self.create_test_device_token(other_account.id, "account2_token")
        
        params = GetDeviceTokensParams(account_id=self.account.id)
        tokens = DeviceTokenService.get_device_tokens_for_account(params=params)
        
        assert len(tokens) == 1
        assert tokens[0].device_token == "account1_token"

    def test_update_device_token_device_info_only(self):
        """Test updating only device_info"""
        token = self.create_test_device_token(self.account.id)

        updated = DeviceTokenService.update_device_token(
            params=UpdateDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token.id,
                device_info={"app_version": "2.0", "os": "Android 12"},
            )
        )

        assert updated.device_info["app_version"] == "2.0"
        assert updated.device_info["os"] == "Android 12"
        assert updated.device_token == token.device_token

    def test_update_device_token_token_only(self):
        """Test updating only device_token"""
        token = self.create_test_device_token(self.account.id, "old_token")

        updated = DeviceTokenService.update_device_token(
            params=UpdateDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token.id,
                device_token="new_token",
            )
        )

        assert updated.device_token == "new_token"
        assert updated.device_info == token.device_info

    def test_update_device_token_both_fields(self):
        """Test updating both device_token and device_info"""
        token = self.create_test_device_token(self.account.id, "old_token")

        updated = DeviceTokenService.update_device_token(
            params=UpdateDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token.id,
                device_token="new_token",
                device_info={"updated": True},
            )
        )

        assert updated.device_token == "new_token"
        assert updated.device_info["updated"] is True

    def test_update_device_token_heartbeat(self):
        """Test heartbeat update (no fields changed)"""
        token = self.create_test_device_token(self.account.id)
        original_last_used = token.last_used_at

        updated = DeviceTokenService.update_device_token(
            params=UpdateDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token.id,
            )
        )

        assert updated.last_used_at is not None
        assert updated.last_used_at >= original_last_used
        assert updated.device_token == token.device_token
        assert updated.device_info == token.device_info

    def test_update_device_token_not_found(self):
        """Test updating non-existent device token"""
        try:
            DeviceTokenService.update_device_token(
                params=UpdateDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id="507f1f77bcf86cd799439011",
                )
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError as exc:
            assert exc.code == DeviceTokenErrorCode.NOT_FOUND

    def test_update_device_token_wrong_account(self):
        """Test updating device from different account"""
        other_account = self.create_test_account("other@example.com")
        token = self.create_test_device_token(other_account.id)

        try:
            DeviceTokenService.update_device_token(
                params=UpdateDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id=token.id,
                    device_info={"hacked": True},
                )
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError:
            pass

    def test_update_device_token_inactive(self):
        """Test updating inactive device token"""
        token = self.create_test_device_token(self.account.id)
        
        DeviceTokenService.deactivate_device_token(
            params=DeleteDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token.id,
            )
        )

        try:
            DeviceTokenService.update_device_token(
                params=UpdateDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id=token.id,
                    device_info={"test": True},
                )
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError:
            pass

    def test_update_device_token_duplicate_conflict(self):
        """Test updating to a device_token that already exists"""
        token1 = self.create_test_device_token(self.account.id, "token_1")
        token2 = self.create_test_device_token(self.account.id, "token_2")

        try:
            DeviceTokenService.update_device_token(
                params=UpdateDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id=token2.id,
                    device_token="token_1",
                )
            )
            assert False, "Expected DeviceTokenConflictError"
        except DeviceTokenConflictError as exc:
            assert exc.code == DeviceTokenErrorCode.CONFLICT

    def test_deactivate_device_token_success(self):
        """Test successful device token deactivation"""
        token = self.create_test_device_token(self.account.id)

        result = DeviceTokenService.deactivate_device_token(
            params=DeleteDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token.id,
            )
        )

        assert result is None

        tokens = DeviceTokenService.get_device_tokens_for_account(
            params=GetDeviceTokensParams(account_id=self.account.id)
        )
        assert len(tokens) == 0

    def test_deactivate_device_token_not_found(self):
        """Test deactivating non-existent device token"""
        try:
            DeviceTokenService.deactivate_device_token(
                params=DeleteDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id="507f1f77bcf86cd799439011",
                )
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError as exc:
            assert exc.code == DeviceTokenErrorCode.NOT_FOUND

    def test_deactivate_device_token_invalid_id(self):
        """Test deactivating with invalid ObjectId format"""
        try:
            DeviceTokenService.deactivate_device_token(
                params=DeleteDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id="not_an_object_id",
                )
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError:
            pass

    def test_deactivate_device_token_wrong_account(self):
        """Test deactivating device from different account"""
        other_account = self.create_test_account("other@example.com")
        token = self.create_test_device_token(other_account.id)

        try:
            DeviceTokenService.deactivate_device_token(
                params=DeleteDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id=token.id,
                )
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError:
            pass

    def test_deactivate_device_token_already_inactive(self):
        """Test deactivating already inactive device"""
        token = self.create_test_device_token(self.account.id)
        
        DeviceTokenService.deactivate_device_token(
            params=DeleteDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token.id,
            )
        )

        try:
            DeviceTokenService.deactivate_device_token(
                params=DeleteDeviceTokenParams(
                    account_id=self.account.id,
                    device_token_id=token.id,
                )
            )
            assert False, "Expected DeviceTokenNotFoundError"
        except DeviceTokenNotFoundError:
            pass

    def test_deactivate_multiple_devices(self):
        """Test deactivating multiple devices"""
        token1 = self.create_test_device_token(self.account.id, "token_1")
        token2 = self.create_test_device_token(self.account.id, "token_2")
        token3 = self.create_test_device_token(self.account.id, "token_3")

        DeviceTokenService.deactivate_device_token(
            params=DeleteDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token1.id,
            )
        )
        DeviceTokenService.deactivate_device_token(
            params=DeleteDeviceTokenParams(
                account_id=self.account.id,
                device_token_id=token3.id,
            )
        )

        tokens = DeviceTokenService.get_device_tokens_for_account(
            params=GetDeviceTokensParams(account_id=self.account.id)
        )
        
        assert len(tokens) == 1
        assert tokens[0].device_token == "token_2"
