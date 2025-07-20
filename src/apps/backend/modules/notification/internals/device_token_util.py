from datetime import datetime
from typing import List

from pymongo.cursor import Cursor


class DeviceTokenUtil:
    @staticmethod
    def extract_tokens_from_cursor(cursor: Cursor) -> List[str]:
        tokens: List[str] = []
        for doc in cursor:
            if doc.get("token"):
                tokens.append(doc["token"])
        return tokens

    @staticmethod
    def get_current_timestamp() -> datetime:
        return datetime.now()
