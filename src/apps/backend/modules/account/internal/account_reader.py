from dataclasses import asdict
from typing import Optional

from bson.objectid import ObjectId

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
    AccountSearchByIdParams,
    AccountSearchParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
)


class AccountReader:
    @staticmethod
    def get_account_by_username(*, username: str) -> Account:
        account_bson = AccountRepository.collection().find_one({"username": username, "active": True})
        if account_bson is None:
            raise AccountWithUsernameNotFoundError(username=username)

        return AccountUtil.convert_account_bson_to_account(account_bson)

    @staticmethod
    def get_account_by_username_and_password(*, params: AccountSearchParams) -> Account:
        account = AccountReader.get_account_by_username(username=params.username)

        if not AccountUtil.compare_password(password=params.password, hashed_password=account.hashed_password):
            raise AccountInvalidPasswordError()
        return account

    @staticmethod
    def get_account_by_id(*, params: AccountSearchByIdParams) -> Account:
        account_bson = AccountRepository.collection().find_one({"_id": ObjectId(params.id), "active": True})
        if account_bson is None:
            raise AccountWithIdNotFoundError(id=params.id)

        return AccountUtil.convert_account_bson_to_account(account_bson)

    @staticmethod
    def check_username_not_exist(*, params: CreateAccountByUsernameAndPasswordParams) -> None:
        account_bson = AccountRepository.collection().find_one({"active": True, "username": params.username})

        if account_bson:
            raise AccountWithUserNameExistsError(username=params.username)

    @staticmethod
    def get_account_by_phone_number_optional(*, phone_number: PhoneNumber) -> Optional[Account]:
        phone_number_dict = asdict(phone_number)
        account_bson = AccountRepository.collection().find_one({"phone_number": phone_number_dict, "active": True})
        if account_bson is None:
            return None

        return AccountUtil.convert_account_bson_to_account(account_bson)

    @staticmethod
    def get_account_by_phone_number(*, phone_number: PhoneNumber) -> Account:
        account = AccountReader.get_account_by_phone_number_optional(phone_number=phone_number)
        if account is None:
            raise AccountWithPhoneNumberNotFoundError(phone_number=phone_number)

        return account

    @staticmethod
    def check_phone_number_not_exist(*, phone_number: PhoneNumber) -> None:
        phone_number_dict = asdict(phone_number)
        account_bson = AccountRepository.collection().find_one({"active": True, "phone_number": phone_number_dict})

        if account_bson:
            raise AccountWithPhoneNumberExistsError(phone_number=phone_number)
