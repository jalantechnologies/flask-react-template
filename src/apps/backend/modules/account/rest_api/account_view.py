from dataclasses import asdict

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.account.types import (
    AccountSearchByIdParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    CreateAccountParams,
    NotificationPreferences,
    PhoneNumber,
    ResetPasswordParams,
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

        if "new_password" in request_data and "token" in request_data:
            reset_account_params = ResetPasswordParams(account_id=id, **request_data)
            account = AccountService.reset_account_password(params=reset_account_params)
            account_dict = asdict(account)
            return jsonify(account_dict), 200

        elif "notification_preferences" in request_data:
            notification_prefs_data = request_data["notification_preferences"]
            notification_preferences = NotificationPreferences(**notification_prefs_data)

            account = AccountService.update_notification_preferences(
                account_id=id, notification_preferences=notification_preferences
            )

            account_dict = asdict(account)
            return jsonify(account_dict), 200

        return (
            jsonify(
                {
                    "error": "Invalid request. Expected 'new_password' and 'token' for password reset, or 'notification_preferences' for preferences update."
                }
            ),
            400,
        )
