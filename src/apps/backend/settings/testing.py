from dataclasses import dataclass, field


@dataclass(frozen=True)
class TestingSettings:
    MONGODB_URI: str = "mongodb://localhost:27017/frm-boilerplate-test"
    MAILER: dict[str, str] = field(
        default_factory=lambda: {
            "default_email": "DEFAULT_EMAIL",
            "default_email_name": "DEFAULT_EMAIL_NAME",
            "forgot_password_mail_template_id": "FORGOT_PASSWORD_MAIL_TEMPLATE_ID",
        }
    )
    SMS_ENABLED: bool = False
    OTP: dict[str, str] = field(
        default_factory=lambda: {
            "exempt_phone_number": "1234567890",
            "exempt_otp": "1234",
        }
    )


@dataclass(frozen=True)
class DockerInstanceTestingSettings:
    MONGODB_URI: str = "mongodb://db:27017/frm-boilerplate-test"
    MAILER: dict[str, str] = field(
        default_factory=lambda: {
            "default_email": "DEFAULT_EMAIL",
            "default_email_name": "DEFAULT_EMAIL_NAME",
            "forgot_password_mail_template_id": "FORGOT_PASSWORD_MAIL_TEMPLATE_ID",
        }
    )
    SMS_ENABLED: bool = False
    OTP: dict[str, str] = field(
        default_factory=lambda: {
            "exempt_phone_number": "1234567890",
            "exempt_otp": "1234",
        }
    )
