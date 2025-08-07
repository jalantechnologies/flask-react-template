import json
from unittest import mock

from server import app

from modules.account.account_service import AccountService
from modules.account.errors import AccountBadRequestError, AccountNotFoundError
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.errors import PasswordResetTokenNotFoundError
from modules.authentication.internals.password_reset_token.password_reset_token_util import PasswordResetTokenUtil
from modules.authentication.internals.password_reset_token.password_reset_token_writer import PasswordResetTokenWriter
from modules.notification.email_service import EmailService
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from tests.modules.authentication.base_test_password_reset_token import BaseTestPasswordResetToken

ACCOUNT_API_URL = "http://127.0.0.1:8080/api/accounts"
PASSWORD_RESET_TOKEN_URL = "http://127.0.0.1:8080/api/password-reset-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestAccountPasswordReset(BaseTestPasswordResetToken):

    # POST /password-reset-tokens tests
    @mock.patch.object(EmailService, "send_email_for_account")
    def test_create_password_reset_token(self, mock_send_email) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        reset_password_params = {"username": account.username}

        with app.test_client() as client:
            response = client.post(PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps(reset_password_params))

            self.assertEqual(response.status_code, 201)
            self.assertTrue(response.json)
            self.assertIn("id", response.json)
            self.assertIn("account", response.json)
            self.assertIn("token", response.json)
            self.assertFalse(response.json["is_used"])
            self.assertTrue(mock_send_email.called)
            self.assertIn("password_reset_link", mock_send_email.call_args.kwargs["params"].template_data)
            self.assertEqual(response.json["account"], account.id)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_create_password_reset_token_account_not_found(self, mock_send_email):
        username = "nonexistent_username@example.com"
        reset_password_params = {"username": username}

        with app.test_client() as client:
            response = client.post(PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps(reset_password_params))

            self.assertEqual(response.status_code, 404)
            self.assertIn("message", response.json)
            self.assertEqual(
                response.json["message"],
                AccountNotFoundError(
                    f"We could not find an account associated with username: {username}. Please verify it or you can create a new account."
                ).message,
            )
            self.assertFalse(mock_send_email.called)

    # PATCH /account/:account_id tests
    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password(self, mock_send_email):
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        token = PasswordResetTokenUtil.generate_password_reset_token()
        PasswordResetTokenWriter.create_password_reset_token(account.id, token)
        AuthenticationService.send_password_reset_email(account.id, account.first_name, account.username, token)

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn("id", response.json)
            self.assertIn("username", response.json)
            self.assertEqual(response.json["id"], account.id)
            self.assertEqual(response.json["username"], account.username)

            # Check if password reset token is marked as used.
            updated_password_reset_token = AuthenticationService.get_password_reset_token_by_account_id(account.id)
            self.assertTrue(updated_password_reset_token.is_used)
            self.assertTrue(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password_account_not_found(self, mock_send_email):
        account_id = "661e42ec98423703a299a899"
        new_password = "new_password"
        token = "token"

        reset_password_params = {"new_password": new_password, "token": token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account_id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )

            self.assertEqual(response.status_code, 404)
            self.assertIn("message", response.json)
            self.assertEqual(
                response.json["message"],
                AccountNotFoundError(
                    f"We could not find an account with id: {account_id}. Please verify and try again."
                ).message,
            )
            self.assertFalse(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password_token_not_found(self, mock_send_email):
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        new_password = "new_password"
        token = "token"

        reset_password_params = {"new_password": new_password, "token": token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )

            self.assertEqual(response.status_code, 404)
            self.assertIn("message", response.json)
            self.assertEqual(response.json["message"], PasswordResetTokenNotFoundError().message)
            self.assertFalse(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password_token_already_used(self, mock_send_email):
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        password_reset_token = AuthenticationService.create_password_reset_token(params=account)

        AuthenticationService.set_password_reset_token_as_used_by_id(password_reset_token.id)

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": password_reset_token.token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )

            self.assertEqual(response.status_code, 400)
            self.assertIn("message", response.json)
            self.assertEqual(
                response.json["message"],
                AccountBadRequestError(
                    f"Password reset is already used for accountId {account.id}. Please retry with new link"
                ).message,
            )
            self.assertTrue(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password_invalid_token(self, mock_send_email):
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        AuthenticationService.create_password_reset_token(params=account)

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": "invalid_token"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )

            self.assertEqual(response.status_code, 400)
            self.assertIn("message", response.json)
            self.assertEqual(
                response.json["message"],
                AccountBadRequestError(
                    f"Password reset link is invalid for accountId {account.id}. Please retry with new link."
                ).message,
            )
            self.assertTrue(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    @mock.patch.object(PasswordResetTokenUtil, "is_token_expired")
    def test_reset_account_password_expired_token(self, mock_is_token_expired, mock_send_email):
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        password_reset_token = AuthenticationService.create_password_reset_token(params=account)

        mock_is_token_expired.return_value = True

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": password_reset_token.token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )

            self.assertEqual(response.status_code, 400)
            self.assertIn("message", response.json)
            self.assertEqual(
                response.json["message"],
                AccountBadRequestError(
                    f"Password reset link is expired for accountId {account.id}. Please retry with new link"
                ).message,
            )
            self.assertTrue(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_password_reset_email_uses_bypass_preferences(self, mock_send_email):
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password123", username="testuser@example.com"
            )
        )

        token = "test_token_123"
        AuthenticationService.send_password_reset_email(
            account_id=account.id, first_name=account.first_name, username=account.username, password_reset_token=token
        )

        mock_send_email.assert_called_once()
        call_kwargs = mock_send_email.call_args.kwargs
        assert call_kwargs["bypass_preferences"] is True
        assert call_kwargs["account_id"] == account.id

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_password_reset_flow_with_disabled_email_preferences(self, mock_send_email):
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="old_password", username="testuser@example.com"
            )
        )

        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id, preferences=CreateOrUpdateAccountNotificationPreferencesParams(email_enabled=False)
        )

        reset_password_params = {"username": account.username}

        with app.test_client() as client:
            response = client.post(PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps(reset_password_params))

            self.assertEqual(response.status_code, 201)
            self.assertTrue(response.json)
            self.assertIn("id", response.json)

        self.assertTrue(mock_send_email.called)
        self.assertTrue(mock_send_email.call_args.kwargs["bypass_preferences"])
