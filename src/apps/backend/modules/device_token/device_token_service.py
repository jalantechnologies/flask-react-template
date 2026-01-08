from modules.logger.logger import Logger
from modules.device_token.errors import InvalidPlatformError
from modules.device_token.internal.device_token_writer import DeviceTokenWriter
from modules.device_token.internal.device_token_reader import DeviceTokenReader
from modules.device_token.types import CreateDeviceTokenParams, DeviceToken, Platform, DeleteDeviceTokenParams, GetDeviceTokensParams, UpdateDeviceTokenParams


class DeviceTokenService:
    @staticmethod
    def create_device_token(*, params: CreateDeviceTokenParams) -> DeviceToken:
        Logger.info(
            message=(
                "Registering device token | "
                f"account_id={params.account_id} | "
                f"platform={params.platform.value} | "
            )
        )

        return DeviceTokenWriter.create_device_token(params=params)
    
    @staticmethod
    def get_device_tokens_for_account(*, params: GetDeviceTokensParams) -> list[DeviceToken]:
        return DeviceTokenReader.get_device_tokens_by_account_id(params=params)
    
    @staticmethod
    def update_device_token(*, params: UpdateDeviceTokenParams) -> DeviceToken:
        if params.device_token or params.device_info:
            Logger.info(message=(
                "Updating device metadata | "
                f"account_id={params.account_id} | "
                f"device_token_id={params.device_token_id}"
            ))
        else:
            Logger.info(message=(
                "Heartbeat device token | "
                f"account_id={params.account_id} | "
                f"device_token_id={params.device_token_id}"
            ))

        return DeviceTokenWriter.update_device_token(params=params)
    
    @staticmethod
    def deactivate_device_token(*, params: DeleteDeviceTokenParams) -> None:
        Logger.info(
            message=(
                f"Unregistering device token | "
                f"account_id={params.account_id} | "
                f"device_token_id={params.device_token_id}"
            )
        )

        return DeviceTokenWriter.deactivate_device_token(params=params)
    