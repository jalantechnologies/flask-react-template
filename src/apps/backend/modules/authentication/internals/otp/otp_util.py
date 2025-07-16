import secrets
import string
from typing import Any, List

from modules.authentication.internals.otp.store.otp_model import OTPModel
from modules.authentication.types import OTP
from modules.config.config_service import ConfigService


class OTPUtil:

    @staticmethod
    def generate_otp(length: int, phone_number: str) -> str:
        if OTPUtil.should_use_default_otp(phone_number):
            default_otp = ConfigService[str].get_value(key="public.default_otp.code")
            return default_otp
        return "".join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def should_use_default_otp(phone_number: str) -> bool:
        is_whitelist_enabled = ConfigService[bool].get_value(key="public.test_whitelist.enabled", default=False)

        if is_whitelist_enabled:
            return OTPUtil.is_phone_number_whitelisted(phone_number)
        else:
            return OTPUtil.is_default_otp_enabled()

    @staticmethod
    def is_phone_number_whitelisted(phone_number: str) -> bool:
        whitelist_numbers = ConfigService[List[str]].get_value(key="public.test_whitelist.phone_numbers", default=[])

        normalized_input = phone_number.replace(" ", "").replace("-", "")

        for whitelisted_number in whitelist_numbers:
            normalized_whitelist = whitelisted_number.replace(" ", "").replace("-", "")
            if normalized_input == normalized_whitelist:
                return True

        return False

    @staticmethod
    def should_send_sms(phone_number: str) -> bool:
        from modules.config.config_service import ConfigService

        is_sms_enabled = ConfigService[bool].get_value(key="sms.enabled", default=True)
        if not is_sms_enabled:
            return False

        if OTPUtil.should_use_default_otp(phone_number):
            return False

        return True

    @staticmethod
    def convert_otp_bson_to_otp(otp_bson: dict[str, Any]) -> OTP:
        validated_otp_data = OTPModel.from_bson(otp_bson)
        return OTP(
            id=str(validated_otp_data.id),
            otp_code=validated_otp_data.otp_code,
            phone_number=validated_otp_data.phone_number,
            status=validated_otp_data.status,
        )

    @staticmethod
    def is_default_otp_enabled() -> bool:
        default_otp_enabled = ConfigService[bool].get_value(key="public.default_otp.enabled", default=False)
        return default_otp_enabled
