from datetime import datetime, timedelta
from typing import Optional

from modules.device_token.types import CreateDeviceTokenParams, DeviceToken, Platform, DeviceTokenDeletionResult, DeleteDeviceTokenParams, GetDeviceTokensParams
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository
from modules.device_token.internal.device_token_reader import DeviceTokenReader
from modules.device_token.internal.device_token_writer import DeviceTokenWriter
from modules.device_token.errors import InvalidPlatformError
from modules.logger.logger import Logger

class DeviceTokenService:
    @staticmethod
    def register_device_token(
        account_id: str,
        device_token: str,
        platform: str,
        device_info: Optional[dict] = None
    ) -> DeviceToken:
        try:
            platform_enum = Platform(platform.lower())
        except ValueError:
            raise InvalidPlatformError(platform)
        
        params = CreateDeviceTokenParams(
            account_id=account_id,
            device_token=device_token.strip(),
            platform=platform_enum,
            device_info=device_info
        )

        Logger.info(
            message=(
                "Registering device token | "
                f"account_id={account_id} | "
                f"platform={platform_enum.value}"
            )
        )

        return DeviceTokenWriter.create_device_token(params=params)
    
    @staticmethod
    def unregister_device_token(account_id: str, device_token_id: str) -> DeviceTokenDeletionResult:
        params = DeleteDeviceTokenParams(
            device_token_id=device_token_id,
            account_id=account_id,
        )

        Logger.info(
            message=(
                f"Unregistering device token | "
                f"account_id={account_id} | "
                f"device_token_id={device_token_id}"
            )
        )

        return DeviceTokenWriter.deactivate_device_token(params=params)
    
    @staticmethod
    def get_device_tokens_for_account(account_id: str, active_only: bool = True) -> list[DeviceToken]:
        params = GetDeviceTokensParams(
            account_id=account_id,
            active_only=active_only,
        )
        
        return DeviceTokenReader.get_device_tokens_by_account_id(params=params)
    
    @staticmethod
    def mark_token_as_invalid(token: str) -> None:
        Logger.warn(
            message=(
                "Marking device token as invalid | "
                f"token_prefix={token[:10] if len(token) >= 10 else token}"
            )
        )

        count = DeviceTokenWriter.deactivate_device_tokens_by_token(token=token)

        Logger.info(
            message=(
                "Deactivated device tokens | "
                f"count={count}"
            )
        )
    
    @staticmethod
    def cleanup_inactive_tokens(days_old: int = 30) -> int:
        cutoff_date = datetime.now() - timedelta(days=days_old)

        Logger.info(
            message=(
                "Starting cleanup of inactive device tokens | "
                f"days_old={days_old} | "
                f"cutoff_date={cutoff_date.isoformat()}"
            )
        )

        result = DeviceTokenRepository.collection().update_many(
            {
                "active": True,
                "$or": [
                    {"last_used_at": {"$lt": cutoff_date}},
                    {
                        "last_used_at": None,
                        "created_at": {"$lt": cutoff_date}
                    }
                ]
            },
            {
                "$set": {
                    "active": False,
                    "updated_at": datetime.now()
                }
            }
        )

        Logger.info(
            message=(
                "Cleaned up inactive device tokens | "
                f"count={result.modified_count}"
            )
        )

        return result.modified_count