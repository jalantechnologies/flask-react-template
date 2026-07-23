from typing import Optional

from modules.account.errors import (
    AccountInvalidPasswordError,
    AccountWithIdNotFoundError,
    AccountWithPhoneNumberExistsError,
    AccountWithPhoneNumberNotFoundError,
    AccountWithUserNameExistsError,
    AccountWithUsernameNotFoundError,
)
from modules.account.internal.account_util import AccountUtil
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import (
    Account,
    AccountQuery,
    AccountSearchByIdParams,
    AccountSearchParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)
from modules.application.common.types import AuditActor


class AccountReader:
    @staticmethod
    def get_account_by_username(*, username: str, actor: AuditActor) -> Account:
        account = AccountRepository.query_one(AccountQuery(username=username), actor=actor)
        if account is None:
            raise AccountWithUsernameNotFoundError(username=username)

        return account

    @staticmethod
    def get_account_by_username_and_password(*, params: AccountSearchParams, actor: AuditActor) -> Account:
        account = AccountReader.get_account_by_username(username=params.username, actor=actor)

        if not AccountUtil.compare_password(password=params.password, hashed_password=account.hashed_password):
            raise AccountInvalidPasswordError()
        return account

    @staticmethod
    def get_account_by_id(*, params: AccountSearchByIdParams, actor: AuditActor) -> Account:
        account = AccountRepository.query_one(AccountQuery(id=params.id), actor=actor)
        if account is None:
            raise AccountWithIdNotFoundError(id=params.id)

        return account

    @staticmethod
    def check_username_not_exist(*, params: CreateAccountByUsernameAndPasswordParams, actor: AuditActor) -> None:
        if AccountRepository.query_one(AccountQuery(username=params.username), actor=actor) is not None:
            raise AccountWithUserNameExistsError(username=params.username)

    @staticmethod
    def get_account_by_phone_number_optional(*, phone_number: PhoneNumber, actor: AuditActor) -> Optional[Account]:
        return AccountRepository.query_one(AccountQuery(phone_number=phone_number), actor=actor)

    @staticmethod
    def get_account_by_phone_number(*, phone_number: PhoneNumber, actor: AuditActor) -> Account:
        account = AccountReader.get_account_by_phone_number_optional(phone_number=phone_number, actor=actor)
        if account is None:
            raise AccountWithPhoneNumberNotFoundError(phone_number=phone_number)

        return account

    @staticmethod
    def check_phone_number_not_exist(*, phone_number: PhoneNumber, actor: AuditActor) -> None:
        if AccountRepository.query_one(AccountQuery(phone_number=phone_number), actor=actor) is not None:
            raise AccountWithPhoneNumberExistsError(phone_number=phone_number)
