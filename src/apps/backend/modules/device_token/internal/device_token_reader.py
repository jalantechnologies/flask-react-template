from modules.device_token.types import DeviceToken, GetDeviceTokensParams
from modules.device_token.internal.device_token_util import DeviceTokenUtil
from modules.device_token.internal.store.device_token_repository import DeviceTokenRepository


class DeviceTokenReader:
    @staticmethod
    def get_device_tokens_by_account_id(*, params: GetDeviceTokensParams) -> list[DeviceToken]:
        device_tokens_bson = list(
            DeviceTokenRepository.collection().find(
                {"account_id": params.account_id, "active": True}).sort([("created_at", -1)]
            )
        )

        return [
            DeviceTokenUtil.convert_device_token_bson_to_device_token(device_token_bson)
            for device_token_bson in device_tokens_bson
        ]
