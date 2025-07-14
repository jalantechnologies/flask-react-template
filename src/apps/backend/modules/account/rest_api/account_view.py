from dataclasses import asdict
from typing import Optional

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
from modules.notification.errors import AccountNotificationPreferencesNotFoundError, ValidationError
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

    def patch(self, id: Optional[str] = None, account_id: Optional[str] = None) -> ResponseReturnValue:
        request_data = request.get_json()

        if id is not None:
            return self._handle_account_update(id, request_data)

        if account_id is not None:
            return self._handle_notification_preferences_update(account_id, request_data)

        raise AccountBadRequestError("Invalid endpoint")

    def _handle_account_update(self, id: str, request_data: dict) -> ResponseReturnValue:
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

    def _handle_notification_preferences_update(self, account_id: str, request_data: dict) -> ResponseReturnValue:
        if not request_data:
            raise AccountBadRequestError("Request body is required")

        self._validate_notification_preferences(request_data)

        preferences_params = CreateOrUpdateAccountNotificationPreferencesParams(
            email_enabled=request_data.get("email_enabled", True),
            push_enabled=request_data.get("push_enabled", True),
            sms_enabled=request_data.get("sms_enabled", True),
        )

        updated_preferences = AccountService.create_or_update_account_notification_preferences(
            account_id=account_id, preferences=preferences_params
        )

        return jsonify(asdict(updated_preferences)), 200

    def _validate_notification_preferences(self, request_data: dict) -> None:
        for field in ["email_enabled", "push_enabled", "sms_enabled"]:
            if field in request_data and not isinstance(request_data[field], bool):
                raise ValidationError(f"{field} must be a boolean")
