import secrets
import string

from modules.config.config_service import ConfigService


class OTPUtil:

    @staticmethod
    def generate_otp(length: int, phone_number: str) -> str:
        if OTPUtil.should_use_default_otp_for_phone_number(phone_number):
            default_otp = ConfigService[str].get_value(key="public.default_otp.code")
            return default_otp
        return "".join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def should_use_default_otp_for_phone_number(phone_number: str) -> bool:
        default_otp_enabled = ConfigService[bool].get_value(key="public.default_otp.enabled", default=False)

        if not default_otp_enabled:
            return False

        has_whitelist_config = ConfigService.has_value(key="public.default_otp.whitelisted_phone_number")

        if not has_whitelist_config:
            return True

        whitelisted_phone_number = ConfigService[str].get_value(
            key="public.default_otp.whitelisted_phone_number", default=""
        )

        if not whitelisted_phone_number:
            return True

        return phone_number == whitelisted_phone_number
