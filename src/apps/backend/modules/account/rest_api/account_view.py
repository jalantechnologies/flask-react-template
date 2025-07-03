from dataclasses import asdict

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.account.errors import AccountBadRequestError
from modules.account.types import (
    AccountSearchByIdParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    CreateAccountParams,
    PhoneNumber,
    ResetPasswordParams,
    UpdateAccountProfileParams,
)
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware


class AccountView(MethodView):
    def post(self) -> ResponseReturnValue:
        request_data = request.get_json()
        account_params: CreateAccountParams
        if "phone_number" in request_data:
            phone_number_data = request_data["phone_number"]
            phone_number_obj = PhoneNumber(**phone_number_data)
            account_params = CreateAccountByPhoneNumberParams(phone_number=phone_number_obj)
            account = AccountService.get_or_create_account_by_phone_number(params=account_params)
        elif "username" in request_data and "password" in request_data:
            account_params = CreateAccountByUsernameAndPasswordParams(**request_data)
            account = AccountService.create_account_by_username_and_password(params=account_params)
        account_dict = asdict(account)
        return jsonify(account_dict), 201

    @access_auth_middleware
    def get(self, id: str) -> ResponseReturnValue:
        account_params = AccountSearchByIdParams(id=id)
        account = AccountService.get_account_by_id(params=account_params)
        account_dict = asdict(account)
        return jsonify(account_dict), 200

    def patch(self, id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if "token" in request_data and "new_password" in request_data:
            reset_account_params = ResetPasswordParams(account_id=id, **request_data)
            account = AccountService.reset_account_password(params=reset_account_params)

        elif "first_name" in request_data or "last_name" in request_data:
            update_profile_params = UpdateAccountProfileParams(
                first_name=request_data.get("first_name", ""), last_name=request_data.get("last_name", "")
            )
            account = AccountService.update_account_profile(account_id=id, params=update_profile_params)

        else:
            raise AccountBadRequestError("Invalid request data")

        account_dict = asdict(account)
        return jsonify(account_dict), 200

    @access_auth_middleware
    def delete(self, id: str) -> ResponseReturnValue:
        account_params = AccountSearchByIdParams(id=id)
        AccountService.delete_account_by_id(params=account_params)
        return jsonify({"message": "Account deleted successfully"}), 200
