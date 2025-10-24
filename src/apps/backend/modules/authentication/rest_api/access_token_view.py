from dataclasses import asdict

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.account.types import AccountSearchParams
from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.types import (
    CreateAccessTokenParams,
    EmailBasedAuthAccessTokenRequestParams,
    OTPBasedAuthAccessTokenRequestParams,
    PhoneNumber,
)


class AccessTokenView(MethodView):
    def post(self) -> ResponseReturnValue:
        request_data = request.get_json()
        access_token_params: CreateAccessTokenParams
        if "phone_number" in request_data and "otp_code" in request_data:
            phone_number_data = request_data["phone_number"]
            phone_number_obj = PhoneNumber(**phone_number_data)
            access_token_params = OTPBasedAuthAccessTokenRequestParams(
                otp_code=request_data["otp_code"], phone_number=phone_number_obj
            )
            account = AccountService.get_account_by_phone_number(phone_number=access_token_params.phone_number)
            access_token = AuthenticationService.create_access_token_by_phone_number(
                params=access_token_params, account=account
            )
        elif "username" in request_data and "password" in request_data:
            access_token_params = EmailBasedAuthAccessTokenRequestParams(**request_data)
            account = AccountService.get_account_by_username_and_password(
                params=AccountSearchParams(username=access_token_params.username, password=access_token_params.password)
            )
            access_token = AuthenticationService.create_access_token_by_username_and_password(account=account)
        access_token_dict = asdict(access_token)
        return jsonify(access_token_dict), 201
