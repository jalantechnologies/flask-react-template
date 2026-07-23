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
from modules.application.common.types import ActorType, AuditActor
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import CreateOTPParams
from modules.notification.notification_service import NotificationService
from modules.notification.types import (
    AccountNotificationPreferences,
    CreateOrUpdateAccountNotificationPreferencesParams,
)

ANONYMOUS_ACTOR = AuditActor(actor_type=ActorType.ANONYMOUS, actor_id=None)


class AccountService:
    @staticmethod
    def create_account_by_username_and_password(*, params: CreateAccountByUsernameAndPasswordParams) -> Account:
        account = AccountWriter.create_account_by_username_and_password(params=params, actor=ANONYMOUS_ACTOR)
        AccountService.create_or_update_account_notification_preferences(
            account_id=account.id,
            actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=account.id),
            preferences=CreateOrUpdateAccountNotificationPreferencesParams(
                email_enabled=True, push_enabled=True, sms_enabled=True
            ),
        )
        return account

    @staticmethod
    def get_account_by_phone_number(*, phone_number: PhoneNumber) -> Account:
        return AccountReader.get_account_by_phone_number(phone_number=phone_number)

    @staticmethod
    def get_or_create_account_by_phone_number(*, params: CreateAccountByPhoneNumberParams) -> Account:
        account = AccountReader.get_account_by_phone_number_optional(phone_number=params.phone_number)

        if account is None:
            account = AccountWriter.create_account_by_phone_number(params=params, actor=ANONYMOUS_ACTOR)
            AccountService.create_or_update_account_notification_preferences(
                account_id=account.id,
                actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=account.id),
                preferences=CreateOrUpdateAccountNotificationPreferencesParams(
                    email_enabled=True, push_enabled=True, sms_enabled=True
                ),
            )

        create_otp_params = CreateOTPParams(phone_number=params.phone_number)
        AuthenticationService.create_otp(params=create_otp_params, account_id=account.id)

        return account

    @staticmethod
    def reset_account_password(*, params: ResetPasswordParams) -> Account:
        account = AccountReader.get_account_by_id(params=AccountSearchByIdParams(id=params.account_id))

        password_reset_token = AuthenticationService.verify_password_reset_token(
            account_id=account.id, token=params.token
        )

        updated_account = AccountWriter.update_password_by_account_id(
            account_id=params.account_id,
            password=params.new_password,
            actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=params.account_id),
        )

        AuthenticationService.set_password_reset_token_as_used_by_id(
            password_reset_token_id=password_reset_token.id, account_id=params.account_id
        )

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
    def get_account_notification_preferences_by_account_id(*, account_id: str) -> AccountNotificationPreferences:
        return NotificationService.get_account_notification_preferences_by_account_id(account_id=account_id)

    @staticmethod
    def delete_account(*, account_id: str, actor: AuditActor) -> AccountDeletionResult:
        return AccountWriter.delete_account(account_id=account_id, actor=actor)
