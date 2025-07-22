import uuid

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.notification.notification_service import NotificationService
from modules.notification.types import DeviceType, RegisterDeviceTokenParams
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
        account = self._create_test_account()

        params = RegisterDeviceTokenParams(account_id=account.id, token="fcm_token_123", device_type=DeviceType.ANDROID)

        device_token = NotificationService.upsert_account_fcm_token(params=params)

        assert device_token.token == "fcm_token_123"
        assert device_token.account_id == account.id
        assert device_token.device_type == DeviceType.ANDROID
        assert device_token.id is not None
        assert device_token.created_at is not None
        assert device_token.updated_at is not None

    def test_get_account_fcm_tokens_multiple_tokens(self) -> None:
        account = self._create_test_account()

        tokens_to_create = [
            ("fcm_token_1", DeviceType.ANDROID),
            ("fcm_token_2", DeviceType.IOS),
            ("fcm_token_3", DeviceType.ANDROID),
        ]

        for token, device_type in tokens_to_create:
            NotificationService.upsert_account_fcm_token(
                params=RegisterDeviceTokenParams(account_id=account.id, token=token, device_type=device_type)
            )

        account_tokens = NotificationService.get_account_fcm_tokens(account.id)

        assert len(account_tokens) == 3
        assert "fcm_token_1" in account_tokens
        assert "fcm_token_2" in account_tokens
        assert "fcm_token_3" in account_tokens

    def test_get_account_fcm_tokens_no_tokens(self) -> None:
        account = self._create_test_account()

        account_tokens = NotificationService.get_account_fcm_tokens(account.id)

        assert account_tokens == []

    def test_get_account_fcm_tokens_different_accounts(self) -> None:
        account1 = self._create_test_account("_1")
        account2 = self._create_test_account("_2")

        NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(
                account_id=account1.id, token="fcm_token_account1", device_type=DeviceType.ANDROID
            )
        )

        NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(
                account_id=account2.id, token="fcm_token_account2", device_type=DeviceType.IOS
            )
        )

        account1_tokens = NotificationService.get_account_fcm_tokens(account1.id)
        account2_tokens = NotificationService.get_account_fcm_tokens(account2.id)

        assert len(account1_tokens) == 1
        assert len(account2_tokens) == 1
        assert "fcm_token_account1" in account1_tokens
        assert "fcm_token_account2" in account2_tokens
        assert "fcm_token_account1" not in account2_tokens
        assert "fcm_token_account2" not in account1_tokens

    def test_delete_account_fcm_tokens_by_account_id_success(self) -> None:
        account = self._create_test_account()

        tokens_to_create = ["fcm_token_1", "fcm_token_2", "fcm_token_3"]
        for i, token in enumerate(tokens_to_create):
            device_type = DeviceType.ANDROID if i % 2 == 0 else DeviceType.IOS
            NotificationService.upsert_account_fcm_token(
                params=RegisterDeviceTokenParams(account_id=account.id, token=token, device_type=device_type)
            )

        account_tokens_before = NotificationService.get_account_fcm_tokens(account.id)
        assert len(account_tokens_before) == 3

        deleted_count = NotificationService.delete_account_fcm_tokens_by_account_id(account.id)

        assert deleted_count == 3

        account_tokens_after = NotificationService.get_account_fcm_tokens(account.id)
        assert len(account_tokens_after) == 0

    def test_delete_account_fcm_tokens_by_account_id_no_tokens(self) -> None:
        account = self._create_test_account()

        deleted_count = NotificationService.delete_account_fcm_tokens_by_account_id(account.id)

        assert deleted_count == 0

    def test_delete_account_fcm_tokens_by_account_id_doesnt_affect_other_accounts(self) -> None:
        account1 = self._create_test_account("_1")
        account2 = self._create_test_account("_2")

        NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(
                account_id=account1.id, token="account1_token", device_type=DeviceType.ANDROID
            )
        )

        NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(account_id=account2.id, token="account2_token", device_type=DeviceType.IOS)
        )

        account1_tokens_before = NotificationService.get_account_fcm_tokens(account1.id)
        account2_tokens_before = NotificationService.get_account_fcm_tokens(account2.id)
        assert len(account1_tokens_before) == 1
        assert len(account2_tokens_before) == 1

        deleted_count = NotificationService.delete_account_fcm_tokens_by_account_id(account1.id)
        assert deleted_count == 1

        account1_tokens_after = NotificationService.get_account_fcm_tokens(account1.id)
        account2_tokens_after = NotificationService.get_account_fcm_tokens(account2.id)
        assert len(account1_tokens_after) == 0
        assert len(account2_tokens_after) == 1
        assert "account2_token" in account2_tokens_after

    def test_get_account_fcm_tokens_nonexistent_account(self) -> None:
        fake_account_id = "661e42ec98423703a299a899"

        account_tokens = NotificationService.get_account_fcm_tokens(fake_account_id)

        assert account_tokens == []

    def test_upsert_device_token_same_account_multiple_devices(self) -> None:
        account = self._create_test_account()

        android_token = NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(
                account_id=account.id, token="fcm_token_android", device_type=DeviceType.ANDROID
            )
        )

        ios_token = NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(account_id=account.id, token="fcm_token_ios", device_type=DeviceType.IOS)
        )

        assert android_token.id != ios_token.id
        assert android_token.account_id == account.id
        assert ios_token.account_id == account.id

        account_tokens = NotificationService.get_account_fcm_tokens(account.id)
        assert len(account_tokens) == 2
        assert "fcm_token_android" in account_tokens
        assert "fcm_token_ios" in account_tokens
