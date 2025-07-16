import secrets
import string
from typing import Any, List

from modules.authentication.internals.otp.store.otp_model import OTPModel
from modules.authentication.types import OTP
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger


class OTPUtil:

    @staticmethod
    def generate_otp(length: int, phone_number: str) -> str:
        if OTPUtil.is_phone_number_whitelisted_for_default_otp(phone_number):
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
    def is_phone_number_whitelisted_for_default_otp(phone_number: str) -> bool:
        default_otp_enabled = ConfigService[bool].get_value(key="public.default_otp.enabled", default=False)

        if not default_otp_enabled:
            return False

        try:
            has_whitelist_config = ConfigService.has_value(
                key="public.default_otp.whitelisted_phone_numbers_with_country_code"
            )

            if not has_whitelist_config:
                return True

            whitelisted_phone_numbers_with_country_code = ConfigService[List[str]].get_value(
                key="public.default_otp.whitelisted_phone_numbers_with_country_code", default=[]
            )

            return phone_number in whitelisted_phone_numbers_with_country_code
        except (TypeError, ValueError, KeyError) as e:
            Logger.warn(
                message=f"Error while checking if phone number '{phone_number}' is whitelisted for default OTP: {type(e).__name__}: {str(e)}"
            )

            return False
