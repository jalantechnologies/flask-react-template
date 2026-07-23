from dataclasses import dataclass
from typing import NotRequired, Optional, TypedDict

from bson import ObjectId

from modules.account.types import PhoneNumber
from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase


class PhoneNumberDocument(TypedDict):
    country_code: str
    phone_number: str


class AccountDocument(StoredDocumentBase):
    active: NotRequired[bool]
    first_name: NotRequired[str]
    hashed_password: NotRequired[str]
    last_name: NotRequired[str]
    phone_number: NotRequired[Optional[PhoneNumberDocument]]
    username: NotRequired[str]


@dataclass
class AccountModel(BaseModel):

    first_name: str
    hashed_password: str
    id: Optional[ObjectId | str]
    last_name: str
    phone_number: Optional[PhoneNumber]
    username: str

    active: bool = True

    def to_bson(self) -> AccountDocument:
        phone_number: Optional[PhoneNumberDocument] = (
            {"country_code": self.phone_number.country_code, "phone_number": self.phone_number.phone_number}
            if self.phone_number is not None
            else None
        )
        doc: AccountDocument = {
            "active": self.active,
            "first_name": self.first_name,
            "hashed_password": self.hashed_password,
            "last_name": self.last_name,
            "phone_number": phone_number,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id if isinstance(self.id, ObjectId) else ObjectId(self.id)
        return doc

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "AccountModel":
        phone_number_data = bson_data.get("phone_number")
        phone_number = PhoneNumber(**phone_number_data) if phone_number_data else None
        return cls(
            active=bson_data.get("active", True),
            first_name=bson_data.get("first_name", ""),
            hashed_password=bson_data.get("hashed_password", ""),
            id=bson_data.get("_id"),
            last_name=bson_data.get("last_name", ""),
            phone_number=phone_number,
            username=bson_data.get("username", ""),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "accounts"
