import json
import uuid

from server import app

from modules.account.account_service import AccountService
from modules.account.types import CreateAccountByUsernameAndPasswordParams
from modules.authentication.types import AccessTokenErrorCode
from modules.notification.notification_service import NotificationService
from modules.notification.types import DeviceType, RegisterDeviceTokenParams
from tests.modules.notification.base_test_notification import BaseTestNotification

DEVICE_TOKEN_URL = "http://127.0.0.1:8080/api/device-tokens"
ACCESS_TOKEN_URL = "http://127.0.0.1:8080/api/access-tokens"
HEADERS = {"Content-Type": "application/json"}


class TestDeviceTokenApi(BaseTestNotification):
    def _create_test_account_and_get_token(self, username_suffix=""):
        unique_id = str(uuid.uuid4())[:8]
        username = f"testuser{username_suffix}_{unique_id}@example.com"

        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="Test", last_name="User", password="password", username=username
            )
        )

        with app.test_client() as client:
            response = client.post(
                ACCESS_TOKEN_URL,
                headers=HEADERS,
                data=json.dumps({"username": account.username, "password": "password"}),
            )
            return account, response.json.get("token")

    def test_register_device_token_success(self) -> None:
        account, token = self._create_test_account_and_get_token()
        device_token_data = {"token": "fcm_token_123", "device_type": DeviceType.ANDROID.value}

        with app.test_client() as client:
            response = client.post(
                DEVICE_TOKEN_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(device_token_data),
            )

            assert response.status_code == 201
            assert response.json
            assert response.json.get("token") == "fcm_token_123"
            assert response.json.get("device_type") == DeviceType.ANDROID.value
            assert response.json.get("account_id") == account.id
            assert "id" in response.json
            assert "created_at" in response.json
            assert "updated_at" in response.json

    def test_register_device_token_ios_success(self) -> None:
        account, token = self._create_test_account_and_get_token()
        device_token_data = {"token": "fcm_token_ios", "device_type": DeviceType.IOS.value}

        with app.test_client() as client:
            response = client.post(
                DEVICE_TOKEN_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(device_token_data),
            )

            assert response.status_code == 201
            assert response.json
            assert response.json.get("token") == "fcm_token_ios"
            assert response.json.get("device_type") == DeviceType.IOS.value
            assert response.json.get("account_id") == account.id

    def test_register_device_token_invalid_device_type(self) -> None:
        account, token = self._create_test_account_and_get_token()
        device_token_data = {"token": "fcm_token_123", "device_type": "web"}

        with app.test_client() as client:
            response = client.post(
                DEVICE_TOKEN_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(device_token_data),
            )

            assert response.status_code == 400
            assert response.json
            assert "Invalid device type" in response.json.get("message", "")
            assert "Must be one of" in response.json.get("message", "")
            assert DeviceType.ANDROID.value in response.json.get("message", "")
            assert DeviceType.IOS.value in response.json.get("message", "")

    def test_register_device_token_without_device_type(self) -> None:
        account, token = self._create_test_account_and_get_token()
        device_token_data = {"token": "fcm_token_123"}

        with app.test_client() as client:
            response = client.post(
                DEVICE_TOKEN_URL,
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                data=json.dumps(device_token_data),
            )

            assert response.status_code == 400
            assert response.json
            assert "Invalid device type" in response.json.get("message", "")

    def test_register_device_token_without_auth(self) -> None:
        device_token_data = {"token": "fcm_token_123", "device_type": DeviceType.ANDROID.value}

        with app.test_client() as client:
            response = client.post(DEVICE_TOKEN_URL, headers=HEADERS, data=json.dumps(device_token_data))

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_delete_all_account_tokens_success(self) -> None:
        account, auth_token = self._create_test_account_and_get_token()

        tokens = ["token1", "token2", "token3"]
        for i, token in enumerate(tokens):
            device_type = DeviceType.ANDROID if i % 2 == 0 else DeviceType.IOS
            NotificationService.upsert_account_fcm_token(
                params=RegisterDeviceTokenParams(account_id=account.id, token=token, device_type=device_type)
            )

        account_tokens = NotificationService.get_account_fcm_tokens(account.id)
        assert len(account_tokens) == 3

        with app.test_client() as client:
            response = client.delete(DEVICE_TOKEN_URL, headers={**HEADERS, "Authorization": f"Bearer {auth_token}"})

            assert response.status_code == 200
            assert response.json
            assert response.json.get("success") is True
            assert response.json.get("deleted_count") == 3

        account_tokens_after = NotificationService.get_account_fcm_tokens(account.id)
        assert len(account_tokens_after) == 0

    def test_delete_tokens_no_existing_tokens(self) -> None:
        account, auth_token = self._create_test_account_and_get_token()

        with app.test_client() as client:
            response = client.delete(DEVICE_TOKEN_URL, headers={**HEADERS, "Authorization": f"Bearer {auth_token}"})

            assert response.status_code == 200
            assert response.json
            assert response.json.get("success") is False
            assert response.json.get("deleted_count") == 0

    def test_delete_tokens_without_auth(self) -> None:
        with app.test_client() as client:
            response = client.delete(DEVICE_TOKEN_URL, headers=HEADERS)

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.AUTHORIZATION_HEADER_NOT_FOUND

    def test_delete_tokens_with_invalid_token(self) -> None:
        with app.test_client() as client:
            response = client.delete(DEVICE_TOKEN_URL, headers={**HEADERS, "Authorization": "Bearer invalid_token"})

            assert response.status_code == 401
            assert response.json
            assert response.json.get("code") == AccessTokenErrorCode.ACCESS_TOKEN_INVALID

    def test_delete_tokens_doesnt_affect_other_accounts(self) -> None:
        account1, auth_token1 = self._create_test_account_and_get_token("_1")
        account2, auth_token2 = self._create_test_account_and_get_token("_2")

        NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(
                account_id=account1.id, token="account1_token", device_type=DeviceType.ANDROID
            )
        )
        NotificationService.upsert_account_fcm_token(
            params=RegisterDeviceTokenParams(account_id=account2.id, token="account2_token", device_type=DeviceType.IOS)
        )

        account1_tokens = NotificationService.get_account_fcm_tokens(account1.id)
        account2_tokens = NotificationService.get_account_fcm_tokens(account2.id)
        assert len(account1_tokens) == 1
        assert len(account2_tokens) == 1

        with app.test_client() as client:
            response = client.delete(DEVICE_TOKEN_URL, headers={**HEADERS, "Authorization": f"Bearer {auth_token1}"})

            assert response.status_code == 200
            assert response.json.get("success") is True
            assert response.json.get("deleted_count") == 1

        account1_tokens_after = NotificationService.get_account_fcm_tokens(account1.id)
        account2_tokens_after = NotificationService.get_account_fcm_tokens(account2.id)
        assert len(account1_tokens_after) == 0
        assert len(account2_tokens_after) == 1
        assert "account2_token" in account2_tokens_after
