import secrets
import string
from typing import Any, List

from modules.authentication.internals.otp.store.otp_model import OTPModel
from modules.authentication.types import OTP
from modules.config.config_service import ConfigService


class OTPUtil:

    @staticmethod
    def generate_otp(length: int, phone_number: str) -> str:
        if OTPUtil.is_default_otp_enabled(phone_number):
            default_otp = ConfigService[str].get_value(key="public.default_otp.code")
            return default_otp
        return "".join(secrets.choice(string.digits) for _ in range(length))

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
    def is_default_otp_enabled(phone_number: str = None) -> bool:
        default_otp_enabled = ConfigService[bool].get_value(key="public.default_otp.enabled", default=False)

        if not default_otp_enabled:
            return False

        if phone_number is None:
            return default_otp_enabled

        try:
            whitelist = ConfigService[List[str]].get_value(key="public.default_otp.whitelist", default=[])
            if not whitelist:
                return True
            return phone_number in whitelist
        except (TypeError, ValueError, KeyError) as e:
            from modules.logger.logger import Logger

            Logger.warn(message=f"Error checking OTP whitelist: {str(e)}")
            return default_otp_enabled
