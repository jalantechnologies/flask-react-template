import json
from datetime import UTC, datetime, timedelta
from unittest import mock
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlparse

from web_app import app

from modules.account.account_service import AccountService
from modules.account.errors import AccountBadRequestError, AccountNotFoundError
from modules.account.types import CreateAccountByUsernameAndPasswordParams, ResetPasswordParams
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.errors import PasswordResetTokenNotFoundError
from modules.authentication.internal.password_reset_token.password_reset_token_util import PasswordResetTokenUtil
from modules.authentication.internal.password_reset_token.password_reset_token_writer import PasswordResetTokenWriter
from modules.authentication.internal.password_reset_token.store.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from modules.authentication.rest_api.password_reset_token_view import PASSWORD_RESET_REQUESTED_MESSAGE
from modules.authentication.types import PasswordResetTokenQuery
from modules.notification.email_service import EmailService
from modules.notification.errors import ServiceError
from modules.notification.notification_service import NotificationService
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams
from tests.conftest import TEST_ACTOR
from tests.modules.authentication.base_test_password_reset_token import BaseTestPasswordResetToken

ACCOUNT_API_URL = "http://127.0.0.1:8080/api/accounts"
PASSWORD_RESET_TOKEN_URL = "http://127.0.0.1:8080/api/password-reset-tokens"
HEADERS = {"Content-Type": "application/json"}


def extract_token_from_password_reset_link(mock_send_email: MagicMock) -> str:
    password_reset_link = mock_send_email.call_args.kwargs["params"].template_data["password_reset_link"]
    return parse_qs(urlparse(password_reset_link).query)["token"][0]


class TestAccountPasswordReset(BaseTestPasswordResetToken):

    # POST /password-reset-tokens tests
    @mock.patch.object(EmailService, "send_email_for_account")
    def test_create_password_reset_token(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        reset_password_params = {"username": account.username}

        with app.test_client() as client:
            response = client.post(PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps(reset_password_params))
            assert response.json is not None

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": PASSWORD_RESET_REQUESTED_MESSAGE})
            self.assertTrue(mock_send_email.called)
            self.assertIn("password_reset_link", mock_send_email.call_args.kwargs["params"].template_data)

        stored_token = AuthenticationService.get_password_reset_token_by_account_id(account.id, actor=TEST_ACTOR)
        self.assertFalse(stored_token.is_used)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_create_password_reset_token_response_omits_the_token_and_account_identifiers(
        self, mock_send_email: MagicMock
    ) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            response = client.post(
                PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": account.username})
            )

        emailed_token = extract_token_from_password_reset_link(mock_send_email)
        stored_token = AuthenticationService.get_password_reset_token_by_account_id(account.id, actor=TEST_ACTOR)
        response_body = response.get_data(as_text=True)

        self.assertTrue(
            PasswordResetTokenUtil.compare_password(password=emailed_token, hashed_password=stored_token.token)
        )
        self.assertNotIn(emailed_token, response_body)
        self.assertNotIn(stored_token.token, response_body)
        self.assertNotIn(stored_token.id, response_body)
        self.assertNotIn(account.id, response_body)
        assert response.json is not None
        self.assertEqual(list(response.json.keys()), ["message"])

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_known_and_unknown_username_produce_identical_password_reset_responses(
        self, mock_send_email: MagicMock
    ) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            known_username = client.post(
                PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": account.username})
            )
            unknown_username = client.post(
                PASSWORD_RESET_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": "nonexistent_username@example.com"}),
            )

        self.assertEqual(known_username.status_code, 200)
        self.assertEqual(unknown_username.status_code, known_username.status_code)
        self.assertEqual(unknown_username.data, known_username.data)
        self.assertEqual(mock_send_email.call_count, 1)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_known_username_response_is_unchanged_when_sending_the_reset_email_fails(
        self, mock_send_email: MagicMock
    ) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            unknown_username = client.post(
                PASSWORD_RESET_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": "nonexistent_username@example.com"}),
            )

            mock_send_email.side_effect = ServiceError("sendgrid is unavailable")
            known_username = client.post(
                PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": account.username})
            )

        self.assertTrue(mock_send_email.called)
        self.assertEqual(known_username.status_code, 200)
        self.assertEqual(known_username.status_code, unknown_username.status_code)
        self.assertEqual(known_username.data, unknown_username.data)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_known_username_response_is_unchanged_when_the_email_transport_times_out(
        self, mock_send_email: MagicMock
    ) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            unknown_username = client.post(
                PASSWORD_RESET_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": "nonexistent_username@example.com"}),
            )

            mock_send_email.side_effect = TimeoutError("connection to the mail transport timed out")
            known_username = client.post(
                PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": account.username})
            )

        self.assertTrue(mock_send_email.called)
        self.assertEqual(known_username.status_code, 200)
        self.assertEqual(known_username.status_code, unknown_username.status_code)
        self.assertEqual(known_username.data, unknown_username.data)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_a_programming_error_while_sending_the_reset_email_is_not_turned_into_a_neutral_response(
        self, mock_send_email: MagicMock
    ) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        mock_send_email.side_effect = TypeError("send_email_for_account() got an unexpected keyword argument")

        with app.test_client() as client:
            response = client.post(
                PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": account.username})
            )

        self.assertEqual(response.status_code, 500)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_emailed_password_reset_token_still_resets_the_password(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        with app.test_client() as client:
            client.post(PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps({"username": account.username}))

            emailed_token = extract_token_from_password_reset_link(mock_send_email)
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}",
                headers=HEADERS,
                data=json.dumps({"new_password": "new_password", "token": emailed_token}),
            )

        self.assertEqual(response.status_code, 200)
        assert response.json is not None
        self.assertEqual(response.json["id"], account.id)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_given_account_when_creating_password_reset_token_then_created_at_and_updated_at_reflect_creation_time(
        self, mock_send_email: MagicMock
    ) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        before = datetime.now(UTC)
        password_reset_token = AuthenticationService.create_password_reset_token(account, actor=TEST_ACTOR)
        after = datetime.now(UTC)

        assert password_reset_token.created_at is not None
        assert password_reset_token.updated_at is not None
        assert password_reset_token.created_at.tzinfo is not None
        assert password_reset_token.updated_at.tzinfo is not None
        assert password_reset_token.created_at.utcoffset() == timedelta(0)
        assert password_reset_token.updated_at.utcoffset() == timedelta(0)
        assert password_reset_token.created_at == password_reset_token.updated_at
        assert before <= password_reset_token.created_at <= after
        assert before <= password_reset_token.updated_at <= after

    def test_given_valid_reset_token_when_resetting_password_then_account_updated_at_reflects_update_time(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )
        token = PasswordResetTokenUtil.generate_password_reset_token()
        PasswordResetTokenWriter.create_password_reset_token(account.id, token, actor=TEST_ACTOR)

        before = datetime.now(UTC)
        updated_account = AccountService.reset_account_password(
            params=ResetPasswordParams(account_id=account.id, new_password="new_password", token=token),
            actor=TEST_ACTOR,
        )
        after = datetime.now(UTC)

        assert updated_account.updated_at is not None
        assert updated_account.created_at is not None
        assert before - timedelta(milliseconds=1) <= updated_account.updated_at <= after
        assert updated_account.updated_at > updated_account.created_at

    def test_given_existing_reset_token_when_marking_used_then_updated_at_reflects_update_time(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )
        token = PasswordResetTokenUtil.generate_password_reset_token()
        PasswordResetTokenWriter.create_password_reset_token(account.id, token, actor=TEST_ACTOR)
        password_reset_token = AuthenticationService.get_password_reset_token_by_account_id(
            account_id=account.id, actor=TEST_ACTOR
        )

        before = datetime.now(UTC)
        used_password_reset_token = AuthenticationService.set_password_reset_token_as_used_by_id(
            password_reset_token.id, actor=TEST_ACTOR
        )
        after = datetime.now(UTC)

        assert used_password_reset_token.is_used
        assert used_password_reset_token.updated_at is not None
        assert used_password_reset_token.created_at is not None
        assert before - timedelta(milliseconds=1) <= used_password_reset_token.updated_at <= after
        assert used_password_reset_token.updated_at > used_password_reset_token.created_at

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_create_password_reset_token_account_not_found(self, mock_send_email: MagicMock) -> None:
        username = "nonexistent_username@example.com"
        reset_password_params = {"username": username}

        with app.test_client() as client:
            response = client.post(PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps(reset_password_params))
            assert response.json is not None

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": PASSWORD_RESET_REQUESTED_MESSAGE})
            self.assertNotIn(username, response.get_data(as_text=True))
            self.assertFalse(mock_send_email.called)

    # PATCH /account/:account_id tests
    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        token = PasswordResetTokenUtil.generate_password_reset_token()
        PasswordResetTokenWriter.create_password_reset_token(account.id, token, actor=TEST_ACTOR)
        AuthenticationService.send_password_reset_email(
            account.id, account.first_name, account.username, token, actor=TEST_ACTOR
        )

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )
            assert response.json is not None

            self.assertEqual(response.status_code, 200)
            self.assertIn("id", response.json)
            self.assertIn("username", response.json)
            self.assertEqual(response.json["id"], account.id)
            self.assertEqual(response.json["username"], account.username)

            # Check if password reset token is marked as used.
            updated_password_reset_token = AuthenticationService.get_password_reset_token_by_account_id(
                account.id, actor=TEST_ACTOR
            )
            self.assertTrue(updated_password_reset_token.is_used)
            self.assertTrue(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password_account_not_found(self, mock_send_email: MagicMock) -> None:
        account_id = "661e42ec98423703a299a899"
        new_password = "new_password"
        token = "token"

        reset_password_params = {"new_password": new_password, "token": token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account_id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )
            assert response.json is not None

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
    def test_reset_account_password_token_not_found(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        new_password = "new_password"
        token = "token"

        reset_password_params = {"new_password": new_password, "token": token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )
            assert response.json is not None

            self.assertEqual(response.status_code, 404)
            self.assertIn("message", response.json)
            self.assertEqual(response.json["message"], PasswordResetTokenNotFoundError().message)
            self.assertFalse(mock_send_email.called)

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_reset_account_password_token_already_used(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        password_reset_token = AuthenticationService.create_password_reset_token(params=account, actor=TEST_ACTOR)

        AuthenticationService.set_password_reset_token_as_used_by_id(password_reset_token.id, actor=TEST_ACTOR)

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": password_reset_token.token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )
            assert response.json is not None

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
    def test_reset_account_password_invalid_token(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        AuthenticationService.create_password_reset_token(params=account, actor=TEST_ACTOR)

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": "invalid_token"}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )
            assert response.json is not None

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
    def test_reset_account_password_expired_token(
        self, mock_is_token_expired: MagicMock, mock_send_email: MagicMock
    ) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )

        password_reset_token = AuthenticationService.create_password_reset_token(params=account, actor=TEST_ACTOR)

        mock_is_token_expired.return_value = True

        new_password = "new_password"

        reset_password_params = {"new_password": new_password, "token": password_reset_token.token}

        with app.test_client() as client:
            response = client.patch(
                f"{ACCOUNT_API_URL}/{account.id}", headers=HEADERS, data=json.dumps(reset_password_params)
            )
            assert response.json is not None

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
    def test_password_reset_email_uses_bypass_preferences(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password123", username="testuser@example.com"
            ),
            actor=TEST_ACTOR,
        )

        token = "test_token_123"
        AuthenticationService.send_password_reset_email(
            account_id=account.id,
            first_name=account.first_name,
            username=account.username,
            password_reset_token=token,
            actor=TEST_ACTOR,
        )

        mock_send_email.assert_called_once()
        call_kwargs = mock_send_email.call_args.kwargs
        assert call_kwargs["bypass_preferences"] is True
        assert call_kwargs["account_id"] == account.id

    @mock.patch.object(EmailService, "send_email_for_account")
    def test_password_reset_flow_with_disabled_email_preferences(self, mock_send_email: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="old_password", username="testuser@example.com"
            ),
            actor=TEST_ACTOR,
        )

        NotificationService.create_or_update_account_notification_preferences(
            account_id=account.id,
            actor=TEST_ACTOR,
            preferences=CreateOrUpdateAccountNotificationPreferencesParams(email_enabled=False),
        )

        reset_password_params = {"username": account.username}

        with app.test_client() as client:
            response = client.post(PASSWORD_RESET_TOKEN_URL, headers=HEADERS, data=json.dumps(reset_password_params))
            assert response.json is not None

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": PASSWORD_RESET_REQUESTED_MESSAGE})

        self.assertTrue(mock_send_email.called)
        self.assertTrue(mock_send_email.call_args.kwargs["bypass_preferences"])

    def test_given_malformed_account_id_when_reading_password_reset_token_then_not_found_is_raised(self) -> None:
        with self.assertRaises(PasswordResetTokenNotFoundError):
            AuthenticationService.get_password_reset_token_by_account_id(account_id="not-a-real-id", actor=TEST_ACTOR)

    def test_given_malformed_account_id_when_querying_password_reset_tokens_then_no_documents_match(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            ),
            actor=TEST_ACTOR,
        )
        token = PasswordResetTokenUtil.generate_password_reset_token()
        PasswordResetTokenWriter.create_password_reset_token(account.id, token, actor=TEST_ACTOR)

        malformed_query = PasswordResetTokenQuery(account_id="not-a-real-id")

        self.assertIsNone(PasswordResetTokenRepository.query_one(malformed_query, actor=TEST_ACTOR))
        self.assertEqual(PasswordResetTokenRepository.query(malformed_query, actor=TEST_ACTOR), [])
        self.assertEqual(PasswordResetTokenRepository.count(malformed_query), 0)
        self.assertEqual(PasswordResetTokenRepository.count(PasswordResetTokenQuery(account_id=account.id)), 1)

    def test_given_malformed_account_id_when_verifying_password_reset_token_then_not_found_is_raised(self) -> None:
        with self.assertRaises(PasswordResetTokenNotFoundError):
            AuthenticationService.verify_password_reset_token(
                account_id="not-a-real-id", token="token", actor=TEST_ACTOR
            )
