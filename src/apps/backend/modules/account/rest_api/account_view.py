from dataclasses import asdict
from typing import Any

from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.account.account_service import AccountService
from modules.account.errors import AccountBadRequestError
from modules.account.types import (
    AccountSearchByIdParams,
    CreateAccountByPhoneNumberParams,
    CreateAccountByUsernameAndPasswordParams,
    ResetPasswordParams,
    UpdateAccountProfileParams,
)
from modules.application.common.types import ActorType, AuditActor
from modules.authentication.rest_api.access_auth_middleware import access_auth_middleware, enforce_account_ownership
from modules.notification.errors import AccountNotificationPreferencesNotFoundError
from modules.notification.types import CreateOrUpdateAccountNotificationPreferencesParams

ANONYMOUS_ACTOR = AuditActor(actor_type=ActorType.ANONYMOUS, actor_id=None)


class AccountView(MethodView):
    @staticmethod
    def _get_request_body_as_object() -> dict[str, Any]:
        request_data = request.get_json()
        if not isinstance(request_data, dict):
            raise AccountBadRequestError("Request body must be a JSON object")
        return request_data

    def post(self) -> ResponseReturnValue:
        request_data = self._get_request_body_as_object()

        if "phone_number" in request_data:
            account = AccountService.get_or_create_account_by_phone_number(
                params=CreateAccountByPhoneNumberParams.from_dict(request_data), actor=ANONYMOUS_ACTOR
            )

        elif "password" in request_data and "username" in request_data:
            account = AccountService.create_account_by_username_and_password(
                params=CreateAccountByUsernameAndPasswordParams.from_dict(request_data), actor=ANONYMOUS_ACTOR
            )

        else:
            raise AccountBadRequestError(
                "Request body must contain either a phone_number object or username and password fields"
            )

        return jsonify(asdict(account)), 201

    @access_auth_middleware
    def get(self, account_id: str) -> ResponseReturnValue:
        actor = AuditActor(actor_type=ActorType.ACCOUNT, actor_id=account_id)
        account_params = AccountSearchByIdParams(id=account_id)
        account = AccountService.get_account_by_id(params=account_params, actor=actor)
        account_dict = asdict(account)

        include_notification_preferences = request.args.get("include_notification_preferences", "").lower() == "true"

        if include_notification_preferences:
            try:
                notification_preferences = AccountService.get_account_notification_preferences_by_account_id(
                    account_id=account.id, actor=actor
                )
                account_dict["notification_preferences"] = asdict(notification_preferences)
            except AccountNotificationPreferencesNotFoundError:
                pass

        return jsonify(account_dict), 200

    def patch(self, account_id: str) -> ResponseReturnValue:
        request_data = self._get_request_body_as_object()

        if "token" in request_data and "new_password" in request_data:
            reset_account_params = ResetPasswordParams(
                account_id=account_id, new_password=request_data["new_password"], token=request_data["token"]
            )
            account = AccountService.reset_account_password(
                params=reset_account_params, actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=account_id)
            )

        elif "first_name" in request_data or "last_name" in request_data:
            enforce_account_ownership(account_id)
            update_profile_params = UpdateAccountProfileParams(
                first_name=request_data.get("first_name"), last_name=request_data.get("last_name")
            )
            account = AccountService.update_account_profile(
                account_id=account_id,
                actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=getattr(request, "account_id")),
                params=update_profile_params,
            )

        else:
            raise AccountBadRequestError("Invalid request data")

        return jsonify(asdict(account)), 200

    @access_auth_middleware
    def delete(self, account_id: str) -> ResponseReturnValue:
        AccountService.delete_account(
            account_id=account_id,
            actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=getattr(request, "account_id")),
        )
        return "", 204

    @staticmethod
    @access_auth_middleware
    def update_account_notification_preferences(account_id: str) -> ResponseReturnValue:
        request_data = AccountView._get_request_body_as_object()

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
            account_id=account_id,
            actor=AuditActor(actor_type=ActorType.ACCOUNT, actor_id=getattr(request, "account_id")),
            preferences=preferences_params,
        )

        return jsonify(asdict(updated_preferences)), 200
