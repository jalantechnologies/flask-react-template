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
from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams


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

        include_notification_preferences = request.args.get("include_notification_preferences", "").lower() == "true"

        if include_notification_preferences:
            try:
                notification_preferences = AccountService.get_account_notification_preferences_by_account_id(
                    account_id=account.id
                )
                account_dict["notification_preferences"] = asdict(notification_preferences)
            except AccountNotificationPreferencesNotFoundError:
                pass

        return jsonify(account_dict), 200

    def patch(self, id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if "token" in request_data and "new_password" in request_data:
            reset_account_params = ResetPasswordParams(account_id=id, **request_data)
            account = AccountService.reset_account_password(params=reset_account_params)

        elif "first_name" in request_data or "last_name" in request_data:
            update_profile_params = UpdateAccountProfileParams(
                first_name=request_data.get("first_name"), last_name=request_data.get("last_name")
            )
            account = AccountService.update_account_profile(account_id=id, params=update_profile_params)

        else:
            raise AccountBadRequestError("Invalid request data")

        account_dict = asdict(account)
        return jsonify(account_dict), 200

    @access_auth_middleware
    def delete(self, id: str) -> ResponseReturnValue:
        AccountService.delete_account(account_id=id)
        return "", 204

    @staticmethod
    def update_account_notification_preferences(account_id: str) -> ResponseReturnValue:
        request_data = request.get_json()

        if request_data is None:
            raise AccountBadRequestError("Request body is required")

        for field in ["email_enabled", "push_enabled", "sms_enabled"]:
            if field in request_data and not isinstance(request_data[field], bool):
                raise AccountBadRequestError(f"{field} must be a boolean")

        preferences_kwargs = {}

        if "email_enabled" in request_data:
            preferences_kwargs["email_enabled"] = request_data["email_enabled"]

        if "push_enabled" in request_data:
            preferences_kwargs["push_enabled"] = request_data["push_enabled"]

        if "sms_enabled" in request_data:
            preferences_kwargs["sms_enabled"] = request_data["sms_enabled"]

        if not preferences_kwargs:
            raise AccountBadRequestError(
                "At least one preference field (email_enabled, push_enabled, sms_enabled) must be provided"
            )

        preferences_params = CreateOrUpdateAccountNotificationPreferencesParams(**preferences_kwargs)

        updated_preferences = AccountService.create_or_update_account_notification_preferences(
            account_id=account_id, preferences=preferences_params
        )

        return jsonify(asdict(updated_preferences)), 200
