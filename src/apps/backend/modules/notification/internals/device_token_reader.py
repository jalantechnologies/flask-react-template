from typing import List

from modules.notification.internals.device_token_util import DeviceTokenUtil
from modules.notification.internals.store.device_token_repository import DeviceTokenRepository


class DeviceTokenReader:
    @staticmethod
    def get_account_fcm_tokens(account_id: str) -> List[str]:
        cursor = DeviceTokenRepository.collection().find({"account_id": account_id})
        return DeviceTokenUtil.extract_tokens_from_cursor(cursor)
