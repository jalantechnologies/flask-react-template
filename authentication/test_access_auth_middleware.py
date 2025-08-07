import unittest
from unittest.mock import MagicMock, patch

from flask import request
from server import app

from modules.authentication.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    AuthorizationHeaderNotFoundError,
    InvalidAuthorizationHeaderError,
    UnauthorizedAccessError,
)
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware

TEST_TOKEN = "your_test_token"


class TestAccessAuthMiddleware(unittest.TestCase):
    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_missing_authorization_header(self, mock_verify_access_token):
        mock_next_func = MagicMock()

        with app.test_request_context():
            with self.assertRaises(AuthorizationHeaderNotFoundError):
                access_auth_middleware(mock_next_func)()

        mock_next_func.assert_not_called()

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_invalid_authorization_header(self, mock_verify_access_token):
        mock_next_func = MagicMock()

        with app.test_request_context():
            request.headers = {"Authorization": f"JWT {TEST_TOKEN}"}
            with self.assertRaises(InvalidAuthorizationHeaderError):
                access_auth_middleware(mock_next_func)()

        mock_next_func.assert_not_called()

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_invalid_access_token(self, mock_verify_access_token):
        mock_next_func = MagicMock()
        mock_verify_access_token.side_effect = AccessTokenInvalidError("Invalid access token.")

        with app.test_request_context():
            request.headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
            with self.assertRaises(AccessTokenInvalidError):
                access_auth_middleware(mock_next_func)()

        mock_next_func.assert_not_called()

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_unauthorized_access(self, mock_verify_access_token):
        mock_verify_access_token.return_value = MagicMock(account_id="12345")

        @access_auth_middleware
        def test_view_func(account_id):
            return account_id

        with app.test_request_context(headers={"Authorization": f"Bearer {TEST_TOKEN}"}):
            with self.assertRaises(UnauthorizedAccessError):
                test_view_func(account_id="67890")

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_expired_access_token(self, mock_verify_access_token):
        mock_next_func = MagicMock()
        mock_verify_access_token.side_effect = AccessTokenExpiredError("Access token has expired. Please login again.")

        with app.test_request_context(headers={"Authorization": f"Bearer {TEST_TOKEN}"}):
            with self.assertRaises(AccessTokenExpiredError):
                access_auth_middleware(mock_next_func)()

        mock_next_func.assert_not_called()
