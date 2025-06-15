from modules.account.internal.account_reader import AccountReader
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import (
    Account,
    AccountSearchByIdParams,
    AccountSearchParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    NotificationPreferences,
    PhoneNumber,
    ResetPasswordParams,
)
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams


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
    def update_notification_preferences(
        *, account_id: str, notification_preferences: NotificationPreferences
    ) -> Account:
        """
        Update notification preferences for a user account

        Args:
            account_id: ID of the account to update
            notification_preferences: NotificationPreferences object with the user's preferences

        Returns:
            Updated Account object
        """
        return AccountWriter.update_notification_preferences(
            account_id=account_id, notification_preferences=notification_preferences
        )

    @staticmethod
    def get_account_by_id(*, params: AccountSearchByIdParams) -> Account:
        return AccountReader.get_account_by_id(params=params)

    @staticmethod
    def get_account_by_username(*, username: str) -> Account:
        return AccountReader.get_account_by_username(username=username)

    @staticmethod
    def get_account_by_username_and_password(*, params: AccountSearchParams) -> Account:
        return AccountReader.get_account_by_username_and_password(params=params)
