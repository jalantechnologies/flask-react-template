from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

from server import app

from modules.account.account_service import AccountService
from modules.account.errors import AccountNotFoundError, AccountWithIdNotFoundError
from modules.account.types import (
    AccountErrorCode,
    AccountSearchByIdParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
    UpdateAccountProfileParams,
)
from modules.authentication.types import AccessTokenPayload
from tests.conftest import TEST_ACTOR
from tests.modules.account.base_test_account import BaseTestAccount


class TestAccountService(BaseTestAccount):
    def test_create_account_by_username_and_password(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                password="password", username="username", first_name="first_name", last_name="last_name"
            )
        )

        assert account.username == "username"
        assert account.first_name == "first_name"
        assert account.last_name == "last_name"

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_get_account_by_id(self, mock_verify_access_token: MagicMock) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        mock_verify_access_token.return_value = AccessTokenPayload(account_id=account.id)

        with app.test_request_context():
            get_account_by_id = AccountService.get_account_by_id(params=AccountSearchByIdParams(id=account.id))

        assert get_account_by_id.username == account.username
        assert get_account_by_id.first_name == account.first_name
        assert get_account_by_id.last_name == account.last_name

    @patch("modules.authentication.authentication_service.AuthenticationService.verify_access_token")
    def test_throw_exception_when_usernot_exist(self, mock_verify_access_token: MagicMock) -> None:
        try:
            mock_verify_access_token.return_value = AccessTokenPayload(account_id="5f7b1b7b4f3b9b1b3f3b9b1b")
            with app.test_request_context():
                AccountService.get_account_by_id(params=AccountSearchByIdParams(id="5f7b1b7b4f3b9b1b3f3b9b1b"))
        except AccountNotFoundError as exc:
            assert exc.code == AccountErrorCode.NOT_FOUND

    def test_get_or_create_account_by_phone_number(self) -> None:
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(
                phone_number=PhoneNumber(**{"country_code": "+91", "phone_number": "9999999999"})
            )
        )

        assert account.phone_number == PhoneNumber(country_code="+91", phone_number="9999999999")

    def test_throw_exception_when_phone_number_not_exist(self) -> None:
        phone_number = PhoneNumber(**{"country_code": "+91", "phone_number": "9999999999"})
        try:
            AccountService.get_account_by_phone_number(phone_number=phone_number)
        except AccountNotFoundError as exc:
            assert exc.code == AccountErrorCode.NOT_FOUND
            assert (
                exc.message
                == f"We could not find an account phone number: {phone_number}. Please verify it or you can create a new account."
            )

    def test_update_account_profile_first_name_only(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                password="password", username="username", first_name="old_first_name", last_name="old_last_name"
            )
        )

        update_params = UpdateAccountProfileParams(first_name="new_first_name")
        updated_account = AccountService.update_account_profile(
            account_id=account.id, actor=TEST_ACTOR, params=update_params
        )

        assert updated_account.id == account.id
        assert updated_account.username == account.username
        assert updated_account.first_name == "new_first_name"
        assert updated_account.last_name == "old_last_name"

    def test_update_account_profile_last_name_only(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                password="password", username="username", first_name="old_first_name", last_name="old_last_name"
            )
        )

        update_params = UpdateAccountProfileParams(last_name="new_last_name")
        updated_account = AccountService.update_account_profile(
            account_id=account.id, actor=TEST_ACTOR, params=update_params
        )

        assert updated_account.id == account.id
        assert updated_account.username == account.username
        assert updated_account.first_name == "old_first_name"
        assert updated_account.last_name == "new_last_name"

    def test_update_account_profile_both_names(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                password="password", username="username", first_name="old_first_name", last_name="old_last_name"
            )
        )

        update_params = UpdateAccountProfileParams(first_name="new_first_name", last_name="new_last_name")
        updated_account = AccountService.update_account_profile(
            account_id=account.id, actor=TEST_ACTOR, params=update_params
        )

        assert updated_account.id == account.id
        assert updated_account.username == account.username
        assert updated_account.first_name == "new_first_name"
        assert updated_account.last_name == "new_last_name"

    def test_update_account_profile_no_changes(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                password="password",
                username="username",
                first_name="original_first_name",
                last_name="original_last_name",
            )
        )

        update_params = UpdateAccountProfileParams(first_name=None, last_name=None)
        updated_account = AccountService.update_account_profile(
            account_id=account.id, actor=TEST_ACTOR, params=update_params
        )

        assert updated_account.id == account.id
        assert updated_account.username == account.username
        assert updated_account.first_name == "original_first_name"
        assert updated_account.last_name == "original_last_name"

    def test_update_account_profile_empty_string_values(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                password="password",
                username="username",
                first_name="original_first_name",
                last_name="original_last_name",
            )
        )

        update_params = UpdateAccountProfileParams(first_name="", last_name="")
        updated_account = AccountService.update_account_profile(
            account_id=account.id, actor=TEST_ACTOR, params=update_params
        )

        assert updated_account.id == account.id
        assert updated_account.username == account.username
        assert updated_account.first_name == ""
        assert updated_account.last_name == ""

    def test_update_account_profile_account_not_found(self) -> None:
        non_existent_account_id = "5f7b1b7b4f3b9b1b3f3b9b1b"

        update_params = UpdateAccountProfileParams(first_name="new_first_name", last_name="new_last_name")

        try:
            AccountService.update_account_profile(
                account_id=non_existent_account_id, actor=TEST_ACTOR, params=update_params
            )
            assert False, "Expected AccountWithIdNotFoundError to be raised"
        except AccountWithIdNotFoundError as exc:
            assert (
                exc.message
                == f"We could not find an account with id: {non_existent_account_id}. Please verify and try again."
            )

    def test_update_account_profile_with_phone_number_account(self) -> None:
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        update_params = UpdateAccountProfileParams(first_name="Phone", last_name="User")
        updated_account = AccountService.update_account_profile(
            account_id=account.id, actor=TEST_ACTOR, params=update_params
        )

        assert updated_account.id == account.id
        assert updated_account.phone_number == phone_number
        assert updated_account.first_name == "Phone"
        assert updated_account.last_name == "User"

    def test_delete_account_success(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        deletion_result = AccountService.delete_account(account_id=account.id, actor=TEST_ACTOR)

        assert deletion_result.account_id == account.id
        assert deletion_result.success is True
        assert deletion_result.deleted_at is not None
        assert isinstance(deletion_result.deleted_at, datetime)

    def test_given_account_details_when_creating_account_then_created_at_and_updated_at_reflect_creation_time(
        self,
    ) -> None:
        before = datetime.now(UTC)
        created_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="timestamp_username"
            )
        )
        after = datetime.now(UTC)

        assert created_account.created_at is not None
        assert created_account.updated_at is not None
        assert created_account.created_at.tzinfo is not None
        assert created_account.updated_at.tzinfo is not None
        assert created_account.created_at.utcoffset() == timedelta(0)
        assert created_account.updated_at.utcoffset() == timedelta(0)
        assert created_account.created_at == created_account.updated_at
        assert before <= created_account.created_at <= after
        assert before <= created_account.updated_at <= after

    def test_given_existing_account_when_updating_profile_then_updated_at_reflects_update_time(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        before = datetime.now(UTC)
        updated_account = AccountService.update_account_profile(
            account_id=account.id, actor=TEST_ACTOR, params=UpdateAccountProfileParams(first_name="updated_first_name")
        )
        after = datetime.now(UTC)

        assert updated_account.updated_at is not None
        assert updated_account.created_at is not None
        assert before - timedelta(milliseconds=1) <= updated_account.updated_at <= after
        assert updated_account.updated_at > updated_account.created_at

    def test_given_existing_account_when_deleting_account_then_deleted_at_reflects_deletion_time_in_utc(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        before = datetime.now(UTC)
        deletion_result = AccountService.delete_account(account_id=account.id, actor=TEST_ACTOR)
        after = datetime.now(UTC)

        assert deletion_result.deleted_at is not None
        assert deletion_result.deleted_at.tzinfo is not None
        assert deletion_result.deleted_at.utcoffset() == timedelta(0)
        assert before <= deletion_result.deleted_at <= after

    def test_delete_account_not_found(self) -> None:
        non_existent_account_id = "5f7b1b7b4f3b9b1b3f3b9b1b"

        try:
            AccountService.delete_account(account_id=non_existent_account_id, actor=TEST_ACTOR)
            assert False, "Expected AccountWithIdNotFoundError to be raised"
        except AccountWithIdNotFoundError as exc:
            assert (
                exc.message
                == f"We could not find an account with id: {non_existent_account_id}. Please verify and try again."
            )

    def test_deleted_account_not_found_by_username(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        deletion_result = AccountService.delete_account(account_id=account.id, actor=TEST_ACTOR)
        assert deletion_result.success is True

        try:
            AccountService.get_account_by_username(username=account.username)
            assert False, "Expected AccountWithUsernameNotFoundError to be raised"
        except AccountNotFoundError as exc:
            assert exc.code == AccountErrorCode.NOT_FOUND

    def test_deleted_account_not_found_by_id(self) -> None:
        account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        deletion_result = AccountService.delete_account(account_id=account.id, actor=TEST_ACTOR)
        assert deletion_result.success is True

        try:
            AccountService.get_account_by_id(params=AccountSearchByIdParams(id=account.id))
            assert False, "Expected AccountWithIdNotFoundError to be raised"
        except AccountNotFoundError as exc:
            assert exc.code == AccountErrorCode.NOT_FOUND

    def test_deleted_phone_number_account_not_found(self) -> None:
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")
        account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        deletion_result = AccountService.delete_account(account_id=account.id, actor=TEST_ACTOR)
        assert deletion_result.success is True

        try:
            AccountService.get_account_by_phone_number(phone_number=phone_number)
            assert False, "Expected AccountWithPhoneNumberNotFoundError to be raised"
        except AccountNotFoundError as exc:
            assert exc.code == AccountErrorCode.NOT_FOUND

    def test_can_create_new_account_with_same_username_after_deletion(self) -> None:
        original_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="first_name", last_name="last_name", password="password", username="username"
            )
        )

        deletion_result = AccountService.delete_account(account_id=original_account.id, actor=TEST_ACTOR)
        assert deletion_result.success is True

        new_account = AccountService.create_account_by_username_and_password(
            params=CreateAccountByUsernameAndPasswordParams(
                first_name="new_first_name", last_name="new_last_name", password="new_password", username="username"
            )
        )

        assert new_account.username == "username"
        assert new_account.first_name == "new_first_name"
        assert new_account.id != original_account.id

    def test_can_create_new_account_with_same_phone_number_after_deletion(self) -> None:
        phone_number = PhoneNumber(country_code="+91", phone_number="9999999999")

        original_account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        deletion_result = AccountService.delete_account(account_id=original_account.id, actor=TEST_ACTOR)
        assert deletion_result.success is True

        new_account = AccountService.get_or_create_account_by_phone_number(
            params=CreateAccountByPhoneNumberParams(phone_number=phone_number)
        )

        assert new_account.phone_number == phone_number
        assert new_account.id != original_account.id
        assert new_account.phone_number.country_code == "+91"
        assert new_account.phone_number.phone_number == "9999999999"
