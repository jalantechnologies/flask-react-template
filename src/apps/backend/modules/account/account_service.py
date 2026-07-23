from modules.account.internal.account_reader import AccountReader
from modules.account.internal.account_writer import AccountWriter
from modules.account.types import (
    Account,
    AccountDeletionResult,
    AccountSearchByIdParams,
    AccountSearchParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    PhoneNumber,
    ResetPasswordParams,
    UpdateAccountProfileParams,
)
from modules.application.common.types import AuditActor
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from modules.notification.notification_service import NotificationService
from modules.notification.types import (
    AccountNotificationPreferences,
    CreateOrUpdateAccountNotificationPreferencesParams,
)


class AccountService:
    @staticmethod
    def create_account_by_username_and_password(
        *, params: CreateAccountByUsernameAndPasswordParams, actor: AuditActor
    ) -> Account:
        account = AccountWriter.create_account_by_username_and_password(params=params, actor=actor)
        AccountService.create_or_update_account_notification_preferences(
            account_id=account.id,
            actor=actor,
            preferences=CreateOrUpdateAccountNotificationPreferencesParams(
                email_enabled=True, push_enabled=True, sms_enabled=True
            ),
        )
        return account

    @staticmethod
    def get_account_by_phone_number(*, phone_number: PhoneNumber, actor: AuditActor) -> Account:
        return AccountReader.get_account_by_phone_number(phone_number=phone_number, actor=actor)

    @staticmethod
    def get_or_create_account_by_phone_number(
        *, params: CreateAccountByPhoneNumberParams, actor: AuditActor
    ) -> Account:
        account = AccountReader.get_account_by_phone_number_optional(phone_number=params.phone_number, actor=actor)

        if account is None:
            account = AccountWriter.create_account_by_phone_number(params=params, actor=actor)
            AccountService.create_or_update_account_notification_preferences(
                account_id=account.id,
                actor=actor,
                preferences=CreateOrUpdateAccountNotificationPreferencesParams(
                    email_enabled=True, push_enabled=True, sms_enabled=True
                ),
            )

        create_otp_params = CreateOTPParams(phone_number=params.phone_number)
        AuthenticationService.create_otp(params=create_otp_params, account_id=account.id, actor=actor)

        return account

    @staticmethod
    def reset_account_password(*, params: ResetPasswordParams, actor: AuditActor) -> Account:
        account = AccountReader.get_account_by_id(params=AccountSearchByIdParams(id=params.account_id), actor=actor)

        password_reset_token = AuthenticationService.verify_password_reset_token(
            account_id=account.id, token=params.token, actor=actor
        )

        updated_account = AccountWriter.update_password_by_account_id(
            account_id=params.account_id, password=params.new_password, actor=actor
        )

        AuthenticationService.set_password_reset_token_as_used_by_id(
            password_reset_token_id=password_reset_token.id, actor=actor
        )

        return updated_account

    @staticmethod
    def get_account_by_id(*, params: AccountSearchByIdParams, actor: AuditActor) -> Account:
        return AccountReader.get_account_by_id(params=params, actor=actor)

    @staticmethod
    def get_account_by_username(*, username: str, actor: AuditActor) -> Account:
        return AccountReader.get_account_by_username(username=username, actor=actor)

    @staticmethod
    def get_account_by_username_and_password(*, params: AccountSearchParams, actor: AuditActor) -> Account:
        return AccountReader.get_account_by_username_and_password(params=params, actor=actor)

    @staticmethod
    def update_account_profile(*, account_id: str, actor: AuditActor, params: UpdateAccountProfileParams) -> Account:
        return AccountWriter.update_account_profile(account_id=account_id, params=params, actor=actor)

    @staticmethod
    def create_or_update_account_notification_preferences(
        *, account_id: str, actor: AuditActor, preferences: CreateOrUpdateAccountNotificationPreferencesParams
    ) -> AccountNotificationPreferences:
        return NotificationService.create_or_update_account_notification_preferences(
            account_id=account_id, actor=actor, preferences=preferences
        )

    @staticmethod
    def get_account_notification_preferences_by_account_id(
        *, account_id: str, actor: AuditActor
    ) -> AccountNotificationPreferences:
        return NotificationService.get_account_notification_preferences_by_account_id(
            account_id=account_id, actor=actor
        )

    @staticmethod
    def delete_account(*, account_id: str, actor: AuditActor) -> AccountDeletionResult:
        return AccountWriter.delete_account(account_id=account_id, actor=actor)
