from dataclasses import asdict
from datetime import UTC, datetime

from phonenumbers import is_valid_number, parse

from modules.account.errors import AccountWithIdNotFoundError
from modules.account.internal.account_reader import AccountReader
from modules.account.internal.account_util import AccountUtil
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import (
    Account,
    AccountDeletionResult,
    AccountQuery,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
    UpdateAccountProfileParams,
)
from modules.application.common.types import AuditActor, ResourceAction
from modules.application.repository import FieldUpdates
from modules.authentication.errors import OTPRequestFailedError


class AccountWriter:
    @staticmethod
    def create_account_by_username_and_password(
        *, params: CreateAccountByUsernameAndPasswordParams, actor: AuditActor
    ) -> Account:
        AccountReader.check_username_not_exist(params=params, actor=actor)
        account = Account(
            id="",
            first_name=params.first_name,
            last_name=params.last_name,
            hashed_password=AccountUtil.hash_password(password=params.password),
            phone_number=None,
            username=params.username,
        )
        return AccountRepository.create(account, actor=actor)

    @staticmethod
    def create_account_by_phone_number(*, params: CreateAccountByPhoneNumberParams, actor: AuditActor) -> Account:
        params_dict = asdict(params)
        phone_number = PhoneNumber(**params_dict["phone_number"])
        is_valid_phone_number = is_valid_number(parse(str(phone_number)))

        if not is_valid_phone_number:
            raise OTPRequestFailedError()

        AccountReader.check_phone_number_not_exist(phone_number=params.phone_number, actor=actor)
        account = Account(
            id="", first_name="", last_name="", hashed_password="", phone_number=phone_number, username=""
        )
        return AccountRepository.create(account, actor=actor)

    @staticmethod
    def update_password_by_account_id(account_id: str, password: str, *, actor: AuditActor) -> Account:
        hashed_password = AccountUtil.hash_password(password=password)
        updated_account = AccountRepository.update(account_id, {"hashed_password": hashed_password}, actor=actor)
        if updated_account is None:
            raise AccountWithIdNotFoundError(id=account_id)

        return updated_account

    @staticmethod
    def update_account_profile(*, account_id: str, params: UpdateAccountProfileParams, actor: AuditActor) -> Account:
        update_fields: FieldUpdates = {}

        if params.first_name is not None:
            update_fields["first_name"] = params.first_name

        if params.last_name is not None:
            update_fields["last_name"] = params.last_name

        updated_account = AccountRepository.update(account_id, update_fields, actor=actor)
        if updated_account is None:
            raise AccountWithIdNotFoundError(id=account_id)

        return updated_account

    @staticmethod
    def delete_account(*, account_id: str, actor: AuditActor) -> AccountDeletionResult:
        deletion_time = datetime.now(UTC)
        deleted = AccountRepository.update_by_query(
            AccountQuery(id=account_id),
            {"active": False, "updated_at": deletion_time},
            actor=actor,
            action=ResourceAction.DELETE,
        )
        if deleted is None:
            raise AccountWithIdNotFoundError(account_id)

        return AccountDeletionResult(account_id=account_id, deleted_at=deletion_time, success=True)
