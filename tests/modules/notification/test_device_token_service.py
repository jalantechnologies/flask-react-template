from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.notification.notification_service import NotificationService
from modules.notification.types import RegisterDeviceTokenParams
from tests.modules.notification.base_test_notification import BaseTestNotification


class TestDeviceTokenService(BaseTestNotification):
    def test_upsert_device_token_new(self) -> None:
        # Create an account
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        # Create a new device token
        token_params = RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-123", device_type="android")

        device_token = NotificationService.upsert_device_token(params=token_params)

        self.assertEqual(device_token.token, "fcm-token-123")
        self.assertEqual(device_token.device_type, "android")
        self.assertEqual(device_token.user_id, account.id)

        # Verify that the token is retrievable
        tokens = NotificationService.get_user_fcm_tokens(account.id)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], "fcm-token-123")

    def test_upsert_device_token_update(self) -> None:
        # Create an account
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        # Create a device token
        token_params = RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-123", device_type="android")

        device_token = NotificationService.upsert_device_token(params=token_params)

        # Update the device token with a new user and device type
        account2 = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name2", last_name="last_name2", password="password2", username="username2"
            )
        )

        updated_token_params = RegisterDeviceTokenParams(user_id=account2.id, token="fcm-token-123", device_type="ios")

        updated_device_token = NotificationService.upsert_device_token(params=updated_token_params)

        self.assertEqual(updated_device_token.token, "fcm-token-123")
        self.assertEqual(updated_device_token.device_type, "ios")
        self.assertEqual(updated_device_token.user_id, account2.id)

        # Verify that the token is no longer associated with the first account
        tokens1 = NotificationService.get_user_fcm_tokens(account.id)
        self.assertEqual(len(tokens1), 0)

        # Verify that the token is now associated with the second account
        tokens2 = NotificationService.get_user_fcm_tokens(account2.id)
        self.assertEqual(len(tokens2), 1)
        self.assertEqual(tokens2[0], "fcm-token-123")

    def test_remove_device_token(self) -> None:
        # Create an account
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        # Create a device token
        token_params = RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-123", device_type="android")

        NotificationService.upsert_device_token(params=token_params)

        # Verify that the token exists
        tokens = NotificationService.get_user_fcm_tokens(account.id)
        self.assertEqual(len(tokens), 1)

        # Remove the token
        result = NotificationService.remove_device_token("fcm-token-123")
        self.assertTrue(result)

        # Verify that the token is gone
        tokens = NotificationService.get_user_fcm_tokens(account.id)
        self.assertEqual(len(tokens), 0)

    def test_remove_nonexistent_device_token(self) -> None:
        # Try to remove a nonexistent token
        result = NotificationService.remove_device_token("nonexistent-token")
        self.assertFalse(result)

    def test_get_user_fcm_tokens_multiple(self) -> None:
        # Create an account
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        # Create multiple device tokens for the account
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-1", device_type="android")
        )
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-2", device_type="ios")
        )
        NotificationService.upsert_device_token(
            params=RegisterDeviceTokenParams(user_id=account.id, token="fcm-token-3", device_type="web")
        )

        # Get the tokens
        tokens = NotificationService.get_user_fcm_tokens(account.id)
        self.assertEqual(len(tokens), 3)
        self.assertIn("fcm-token-1", tokens)
        self.assertIn("fcm-token-2", tokens)
        self.assertIn("fcm-token-3", tokens)

    def test_get_user_fcm_tokens_empty(self) -> None:
        # Create an account
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        # Get the tokens for an account with no tokens
        tokens = NotificationService.get_user_fcm_tokens(account.id)
        self.assertEqual(len(tokens), 0)
