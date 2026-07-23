from dataclasses import dataclass
from typing import NotRequired, Optional, TypedDict

from bson import ObjectId

from modules.account.types import PhoneNumber
from modules.core.base_model import BaseModel, StoredDocument, StoredDocumentBase


class OTPPhoneNumberDocument(TypedDict):
    country_code: str
    phone_number: str


class OTPDocument(StoredDocumentBase):
    active: NotRequired[bool]
    otp_code: NotRequired[str]
    phone_number: NotRequired[OTPPhoneNumberDocument]
    status: NotRequired[str]


@dataclass
class OTPModel(BaseModel):
    active: bool
    id: Optional[ObjectId | str]
    otp_code: str
    phone_number: PhoneNumber
    status: str

    def to_bson(self) -> OTPDocument:
        doc: OTPDocument = {
            "active": self.active,
            "otp_code": self.otp_code,
            "phone_number": {
                "country_code": self.phone_number.country_code,
                "phone_number": self.phone_number.phone_number,
            },
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            doc["_id"] = self.id if isinstance(self.id, ObjectId) else ObjectId(self.id)
        return doc

    @classmethod
    def from_bson(cls, bson_data: StoredDocument) -> "OTPModel":
        phone_number_data = bson_data.get("phone_number")
        if not phone_number_data:
            raise ValueError("Phone number data is required for OTPModel")
        phone_number = PhoneNumber(**phone_number_data)
        return cls(
            active=bson_data.get("active", False),
            id=bson_data.get("_id"),
            otp_code=bson_data.get("otp_code", ""),
            phone_number=phone_number,
            status=bson_data.get("status", ""),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
        )

    @staticmethod
    def get_collection_name() -> str:
        return "otps"
