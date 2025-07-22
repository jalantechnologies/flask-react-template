from dataclasses import asdict
from datetime import datetime

from bson.objectid import ObjectId
from phonenumbers import is_valid_number, parse
from pymongo import ReturnDocument

from modules.account.errors import AccountWithIdNotFoundError
from modules.account.internal.account_reader import AccountReader
from modules.account.internal.account_util import AccountUtil
from modules.account.internal.store.account_model import AccountModel
from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import (
    Account,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
    UpdateAccountProfileParams,
    AccountDeletionResult,
)
from modules.authentication.errors import OTPRequestFailedError
from modules.application.internal.account_deletion_registry import AccountDeletionRegistry
from modules.logger.logger import Logger


class AccountWriter:
    @staticmethod
    def create_account_by_username_and_password(*, params: CreateAccountByUsernameAndPasswordParams) -> Account:
        params_dict = asdict(params)
        params_dict["hashed_password"] = AccountUtil.hash_password(password=params.password)
        del params_dict["password"]
        AccountReader.check_username_not_exist(params=params)
        account_bson = AccountModel(
            first_name=params.first_name,
            hashed_password=params_dict["hashed_password"],
            id=None,
            last_name=params.last_name,
            phone_number=None,
            username=params.username,
        ).to_bson()
        query = AccountRepository.collection().insert_one(account_bson)
        account_bson = AccountRepository.collection().find_one({"_id": query.inserted_id})

        return AccountUtil.convert_account_bson_to_account(account_bson)

    @staticmethod
    def create_account_by_phone_number(*, params: CreateAccountByPhoneNumberParams) -> Account:
        params_dict = asdict(params)
        phone_number = PhoneNumber(**params_dict["phone_number"])
        is_valid_phone_number = is_valid_number(parse(str(phone_number)))

        if not is_valid_phone_number:
            raise OTPRequestFailedError()

        AccountReader.check_phone_number_not_exist(phone_number=params.phone_number)
        account_bson = AccountModel(
            first_name="", hashed_password="", id=None, last_name="", phone_number=phone_number, username=""
        ).to_bson()
        query = AccountRepository.collection().insert_one(account_bson)
        account_bson = AccountRepository.collection().find_one({"_id": query.inserted_id})

        return AccountUtil.convert_account_bson_to_account(account_bson)

    @staticmethod
    def update_password_by_account_id(account_id: str, password: str) -> Account:
        hashed_password = AccountUtil.hash_password(password=password)
        updated_account = AccountRepository.collection().find_one_and_update(
            {"_id": ObjectId(account_id)},
            {"$set": {"hashed_password": hashed_password}},
            return_document=ReturnDocument.AFTER,
        )
        if updated_account is None:
            raise AccountWithIdNotFoundError(id=account_id)

        return AccountUtil.convert_account_bson_to_account(updated_account)

    @staticmethod
    def update_account_profile(*, account_id: str, params: UpdateAccountProfileParams) -> Account:
        update_fields = {}

        if params.first_name is not None:
            update_fields["first_name"] = params.first_name

        if params.last_name is not None:
            update_fields["last_name"] = params.last_name

        updated_account = AccountRepository.collection().find_one_and_update(
            {"_id": ObjectId(account_id)}, {"$set": update_fields}, return_document=ReturnDocument.AFTER
        )
        if updated_account is None:
            raise AccountWithIdNotFoundError(id=account_id)

        return AccountUtil.convert_account_bson_to_account(updated_account)

    @staticmethod
    def delete_account(*, account_id: str) -> AccountDeletionResult:

        Logger.info(message=f"Starting account deletion process for account {account_id}")

        try:
            account_bson = AccountRepository.collection().find_one({"_id": ObjectId(account_id), "active": True})

            if account_bson is None:
                Logger.warn(message=f"Account {account_id} not found or already deleted")
                return AccountDeletionResult(
                    account_id=account_id,
                    success=False,
                    cleanup_results={},
                    message="Account not found or already deleted",
                )

            update_result = AccountRepository.collection().update_one(
                {"_id": ObjectId(account_id)},
                {"$set": {"active": False, "updated_at": datetime.now(), "deleted_at": datetime.now()}},
            )

            if update_result.modified_count == 0:
                Logger.error(message=f"Failed to soft delete account {account_id}")
                return AccountDeletionResult(
                    account_id=account_id, success=False, cleanup_results={}, message="Failed to delete account"
                )

            Logger.info(message=f"Successfully soft deleted account {account_id}")

            cleanup_results = AccountDeletionRegistry.execute_all_hooks(account_id)

            failed_cleanups = [hook_name for hook_name, success in cleanup_results.items() if not success]

            if failed_cleanups:
                Logger.warn(message=f"Some cleanup hooks failed for account {account_id}: {failed_cleanups}")
                message = f"Account deleted with some cleanup failures: {', '.join(failed_cleanups)}"
            else:
                message = "Account successfully deleted"

            Logger.info(message=f"Account deletion process completed for account {account_id}")

            return AccountDeletionResult(
                account_id=account_id, success=True, cleanup_results=cleanup_results, message=message
            )

        except Exception as e:
            Logger.error(message=f"Account deletion failed for account {account_id}: {str(e)}")
            return AccountDeletionResult(
                account_id=account_id, success=False, cleanup_results={}, message=f"Account deletion failed: {str(e)}"
            )
