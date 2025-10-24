from dataclasses import asdict

from pymongo import ReturnDocument

from modules.account.types import PhoneNumber
from modules.authentication.errors import OTPExpiredError, OTPIncorrectError
from modules.authentication.internals.otp.otp_util import OTPUtil
from modules.authentication.internals.otp.store.otp_model import OTPModel
from modules.authentication.internals.otp.store.otp_repository import OTPRepository
from modules.authentication.types import OTP, CreateOTPParams, OTPStatus, VerifyOTPParams


class OTPWriter:
    @staticmethod
    def expire_previous_otps(phone_number: PhoneNumber) -> None:
        phone_number_dict = asdict(phone_number)
        previous_otps = OTPRepository.collection().find({"active": True, "phone_number": phone_number_dict})
        for otp in previous_otps:
            OTPRepository.collection().update_one(
                {"_id": otp["_id"]}, {"$set": {"active": False, "status": OTPStatus.EXPIRED}}
            )

    @staticmethod
    def create_new_otp(*, params: CreateOTPParams) -> OTP:
        OTPWriter.expire_previous_otps(phone_number=params.phone_number)
        phone_number = PhoneNumber(**asdict(params)["phone_number"])
        otp_code = OTPUtil.generate_otp(length=4, phone_number=phone_number.phone_number)
        otp_bson = OTPModel(
            active=True, id=None, phone_number=phone_number, otp_code=otp_code, status=str(OTPStatus.PENDING)
        ).to_bson()
        query = OTPRepository.collection().insert_one(otp_bson)
        otp_bson = OTPRepository.collection().find_one({"_id": query.inserted_id})
        return OTPUtil.convert_otp_bson_to_otp(otp_bson)

    @staticmethod
    def verify_otp(*, params: VerifyOTPParams) -> OTP:
        phone_number_dict = asdict(params.phone_number)
        otp_bson = OTPRepository.collection().find_one(
            {"otp_code": params.otp_code, "phone_number": phone_number_dict}, sort=[("_id", -1)]
        )
        if otp_bson is None:
            raise OTPIncorrectError()

        if not otp_bson["active"]:
            raise OTPExpiredError()

        updated_otp_bson = OTPRepository.collection().find_one_and_update(
            {"_id": otp_bson["_id"]},
            {"$set": {"active": False, "status": OTPStatus.SUCCESS}},
            return_document=ReturnDocument.AFTER,
        )
        return OTPUtil.convert_otp_bson_to_otp(updated_otp_bson)
