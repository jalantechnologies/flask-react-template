from typing import List

from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository
from modules.notification.types import DeviceToken


class DeviceTokenReader:
    @staticmethod
    def get_account_fcm_tokens(account_id: str) -> List[DeviceToken]:
        cursor = DeviceTokenRepository.collection().find({"account_id": account_id})
        return DeviceTokenUtil.convert_cursor_to_device_token_list(cursor)
