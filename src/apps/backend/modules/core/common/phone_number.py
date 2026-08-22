from dataclasses import dataclass
from typing import Any

from modules.core.errors import MalformedPhoneNumberError


@dataclass(frozen=True)
class PhoneNumber:
    country_code: str
    phone_number: str

    def __str__(self) -> str:
        return f"{self.country_code} {self.phone_number}"

    @classmethod
    def from_dict(cls, phone_number_data: Any) -> "PhoneNumber":
        if not isinstance(phone_number_data, dict):
            raise MalformedPhoneNumberError("phone_number must be a JSON object")
        for field_name in ("country_code", "phone_number"):
            if not isinstance(phone_number_data.get(field_name), str):
                raise MalformedPhoneNumberError(f"phone_number.{field_name} must be a string")
        return cls(country_code=phone_number_data["country_code"], phone_number=phone_number_data["phone_number"])
