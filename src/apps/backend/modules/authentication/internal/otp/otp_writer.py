from dataclasses import asdict

from modules.account.types import PhoneNumber
from modules.application.common.types import AuditActor
from modules.authentication.errors import OTPExpiredError, OTPIncorrectError
from modules.authentication.internal.otp.otp_util import OTPUtil
from modules.authentication.internal.otp.store.otp_repository import OTPRepository
from modules.authentication.types import OTP, CreateOTPParams, OTPQuery, OTPStatus, VerifyOTPParams


class OTPWriter:
    @staticmethod
    def expire_previous_otps(phone_number: PhoneNumber, *, actor: AuditActor) -> None:
        previous_otps = OTPRepository.query(OTPQuery(phone_number=phone_number, active=True))
        for otp in previous_otps:
            OTPRepository.update_fields(otp.id, {"active": False, "status": str(OTPStatus.EXPIRED)}, actor=actor)

    @staticmethod
    def create_new_otp(*, params: CreateOTPParams, actor: AuditActor) -> OTP:
        OTPWriter.expire_previous_otps(phone_number=params.phone_number, actor=actor)
        phone_number = PhoneNumber(**asdict(params)["phone_number"])
        otp_code = OTPUtil.generate_otp(length=4, phone_number=phone_number.phone_number)
        otp = OTP(id="", otp_code=otp_code, phone_number=phone_number, status=str(OTPStatus.PENDING), active=True)
        return OTPRepository.create(otp, actor=actor)

    @staticmethod
    def verify_otp(*, params: VerifyOTPParams, actor: AuditActor) -> OTP:
        # Newest first, so a stale code resolves to the most recent attempt; matches the previous _id sort.
        otp = OTPRepository.query_one(
            OTPQuery(otp_code=params.otp_code, phone_number=params.phone_number), sort=[("_id", -1)]
        )
        if otp is None:
            raise OTPIncorrectError()

        # A correct-but-already-consumed code is "expired", distinct from an incorrect code above.
        if not otp.active:
            raise OTPExpiredError()

        updated_otp = OTPRepository.update(otp.id, {"active": False, "status": str(OTPStatus.SUCCESS)}, actor=actor)
        # update() returns None only if the row vanished between the read and the patch; the read above
        # found it, so it is present here.
        assert updated_otp is not None
        return updated_otp
