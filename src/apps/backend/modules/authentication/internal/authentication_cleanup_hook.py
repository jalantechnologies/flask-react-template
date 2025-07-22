from modules.application.internal.account_deletion_registry import BaseAccountDeletionHook
from modules.authentication.internals.otp.store.otp_repository import OTPRepository
from modules.authentication.internals.password_reset_token.store.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from modules.logger.logger import Logger
from bson.objectid import ObjectId


class AuthenticationCleanupHook(BaseAccountDeletionHook):

    @property
    def hook_name(self) -> str:
        return "authentication_cleanup"

    def execute(self, account_id: str) -> None:
        Logger.info(message=f"Starting authentication data cleanup for account {account_id}")

        self._cleanup_otp_records(account_id)

        self._cleanup_password_reset_tokens(account_id)

        Logger.info(message=f"Authentication data cleanup completed for account {account_id}")

    def _cleanup_otp_records(self, account_id: str) -> None:
        try:

            result = OTPRepository.collection().update_many(
                {"active": True}, {"$set": {"active": False, "status": "ACCOUNT_DELETED"}}
            )
            Logger.info(message=f"Deactivated {result.modified_count} OTP records during account cleanup")

        except Exception as e:
            Logger.error(message=f"Failed to cleanup OTP records for account {account_id}: {str(e)}")
            raise

    def _cleanup_password_reset_tokens(self, account_id: str) -> None:
        try:
            result = PasswordResetTokenRepository.collection().delete_many({"account": ObjectId(account_id)})
            Logger.info(message=f"Deleted {result.deleted_count} password reset tokens for account {account_id}")

        except Exception as e:
            Logger.error(message=f"Failed to cleanup password reset tokens for account {account_id}: {str(e)}")
            raise
