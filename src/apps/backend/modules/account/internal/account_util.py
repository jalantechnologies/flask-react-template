from typing import Any

import bcrypt

from modules.account.internal.store.account_model import AccountModel
from modules.account.types import Account


class AccountUtil:
    @staticmethod
    def hash_password(*, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode()

    @staticmethod
    def compare_password(*, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def convert_account_bson_to_account(account_bson: dict[str, Any]) -> Account:
        validated_account_data = AccountModel.from_bson(account_bson)
        return Account(
            first_name=validated_account_data.first_name,
            id=str(validated_account_data.id),
            last_name=validated_account_data.last_name,
            hashed_password=validated_account_data.hashed_password,
            phone_number=validated_account_data.phone_number,
            username=validated_account_data.username,
        )
