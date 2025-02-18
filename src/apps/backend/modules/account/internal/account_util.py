import bcrypt

from modules.account.internal.store.account_model import AccountModel
from modules.account.types import Account, AccountWithPassword


class AccountUtil:
    @staticmethod
    def hash_password(*, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def compare_password(*, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def convert_account_model_to_account(account_model: AccountModel) -> Account:
        return Account(
            id=str(account_model.id),
            first_name=account_model.first_name,
            last_name=account_model.last_name,
            phone_number=account_model.phone_number,
            username=account_model.username,
        )
    
    @staticmethod
    def convert_account_model_to_account_password(account_model: AccountModel) -> AccountWithPassword:
        return AccountWithPassword(
            id=str(account_model.id),
            first_name=account_model.first_name,
            last_name=account_model.last_name,
            phone_number=account_model.phone_number,
            username=account_model.username,
            password=account_model.hashed_password
        )
