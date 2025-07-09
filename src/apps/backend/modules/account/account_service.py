from datetime import datetime

from modules.account.internal.account_reader import AccountReader
from modules.account.internal.account_writer import AccountWriter
from modules.account.internal.store.account_notification_preferences_model import AccountNotificationPreferencesModel
from modules.account.internal.store.account_notification_preferences_repository import (
    AccountNotificationPreferencesRepository,
)
from modules.account.types import (
    Account,
    AccountSearchByIdParams,
    AccountSearchParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
    ResetPasswordParams,
    UpdateAccountProfileParams,
)
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from modules.notification.types import NotificationPreferences, UpdateNotificationPreferencesParams


class AccountService:
    @staticmethod
    def create_account_by_username_and_password(*, params: CreateAccountByUsernameAndPasswordParams) -> Account:
        return AccountWriter.create_account_by_username_and_password(params=params)

    @staticmethod
    def get_account_by_phone_number(*, phone_number: PhoneNumber) -> Account:
        return AccountReader.get_account_by_phone_number(phone_number=phone_number)

    @staticmethod
    def get_or_create_account_by_phone_number(*, params: CreateAccountByPhoneNumberParams) -> Account:
        account = AccountReader.get_account_by_phone_number_optional(phone_number=params.phone_number)

        if account is None:
            account = AccountWriter.create_account_by_phone_number(params=params)

        create_otp_params = CreateOTPParams(phone_number=params.phone_number)
        AuthenticationService.create_otp(params=create_otp_params)

        return account

    @staticmethod
    def reset_account_password(*, params: ResetPasswordParams) -> Account:
        account = AccountReader.get_account_by_id(params=AccountSearchByIdParams(id=params.account_id))

        password_reset_token = AuthenticationService.verify_password_reset_token(
            account_id=account.id, token=params.token
        )

        updated_account = AccountWriter.update_password_by_account_id(
            account_id=params.account_id, password=params.new_password
        )

        AuthenticationService.set_password_reset_token_as_used_by_id(password_reset_token_id=password_reset_token.id)

        return updated_account

    @staticmethod
    def get_account_by_id(*, params: AccountSearchByIdParams) -> Account:
        return AccountReader.get_account_by_id(params=params)

    @staticmethod
    def get_account_by_username(*, username: str) -> Account:
        return AccountReader.get_account_by_username(username=username)

    @staticmethod
    def get_account_by_username_and_password(*, params: AccountSearchParams) -> Account:
        return AccountReader.get_account_by_username_and_password(params=params)

    @staticmethod
    def get_notification_preferences(account_id: str) -> NotificationPreferences:

        notification_preferences = AccountNotificationPreferencesRepository.collection().find_one(
            {"account_id": account_id}
        )

        if notification_preferences is None:
            default_preferences = AccountNotificationPreferencesModel(account_id=account_id, id=None).to_bson()
            AccountNotificationPreferencesRepository.collection().insert_one(default_preferences)
            return NotificationPreferences()

        preferences_model = AccountNotificationPreferencesModel.from_bson(notification_preferences)
        return NotificationPreferences(
            email_enabled=preferences_model.email_enabled,
            push_enabled=preferences_model.push_enabled,
            sms_enabled=preferences_model.sms_enabled,
        )

    @staticmethod
    def update_notification_preferences(params: UpdateNotificationPreferencesParams) -> NotificationPreferences:

        existing_preferences = AccountNotificationPreferencesRepository.collection().find_one(
            {"account_id": params.account_id}
        )

        update_data = {
            "email_enabled": params.email_enabled,
            "push_enabled": params.push_enabled,
            "sms_enabled": params.sms_enabled,
            "updated_at": datetime.now(),
        }

        if existing_preferences is None:
            preferences_model = AccountNotificationPreferencesModel(
                account_id=params.account_id,
                id=None,
                email_enabled=params.email_enabled,
                push_enabled=params.push_enabled,
                sms_enabled=params.sms_enabled,
            ).to_bson()
            AccountNotificationPreferencesRepository.collection().insert_one(preferences_model)
        else:
            AccountNotificationPreferencesRepository.collection().update_one(
                {"account_id": params.account_id}, {"$set": update_data}
            )

        return NotificationPreferences(
            email_enabled=params.email_enabled, push_enabled=params.push_enabled, sms_enabled=params.sms_enabled
        )

    @staticmethod
    def update_account_profile(*, account_id: str, params: UpdateAccountProfileParams) -> Account:
        return AccountWriter.update_account_profile(account_id=account_id, params=params)
