from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from modules.authentication.authentication_service import AuthenticationService
from modules.authentication.errors import AuthorizationHeaderNotFoundError, InvalidAuthorizationHeaderError
from modules.logger.logger import Logger
from modules.notification.fcm_token_service import FCMTokenService
from modules.notification.types import AddFCMTokenParams, DeleteFCMTokenParams, GetFCMTokensParams


class FCMTokenView(MethodView):
    """View controller for FCM token management endpoints"""

    methods = ["GET", "POST", "DELETE"]

    def _get_account_id_from_token(self) -> str:
        """Extract account_id from the authorization token"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AuthorizationHeaderNotFoundError("Authorization header is missing.")

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer" or not parts[1]:
            raise InvalidAuthorizationHeaderError("Invalid authorization header.")

        token = parts[1]
        auth_payload = AuthenticationService.verify_access_token(token=token)
        return auth_payload.account_id

    def get(self) -> ResponseReturnValue:
        """Get all FCM tokens for the authenticated user"""
        try:
            account_id = self._get_account_id_from_token()
            params = GetFCMTokensParams(user_id=account_id)

            result = FCMTokenService.get_tokens(params)

            if result.get("success", False):
                return jsonify(result), 200
            else:
                return jsonify(result), 400

        except (AuthorizationHeaderNotFoundError, InvalidAuthorizationHeaderError) as e:
            return jsonify({"success": False, "error": "Authentication failed", "message": str(e)}), 401
        except Exception as e:
            Logger.error(message=f"Error in FCM token GET endpoint: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error", "message": str(e)}), 500

    def post(self) -> ResponseReturnValue:
        """Add a new FCM token for the authenticated user"""
        try:
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            request_data = request.get_json()

            if "fcm_token" not in request_data:
                return jsonify({"error": "Missing required field: fcm_token"}), 400

            account_id = self._get_account_id_from_token()

            params = AddFCMTokenParams(
                user_id=account_id, fcm_token=request_data["fcm_token"], device_info=request_data.get("device_info")
            )

            result = FCMTokenService.add_token(params)

            if result.get("success", False):
                return jsonify(result), 200
            else:
                return jsonify(result), 400

        except (AuthorizationHeaderNotFoundError, InvalidAuthorizationHeaderError) as e:
            return jsonify({"success": False, "error": "Authentication failed", "message": str(e)}), 401
        except Exception as e:
            Logger.error(message=f"Error in FCM token POST endpoint: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error", "message": str(e)}), 500

    def delete(self) -> ResponseReturnValue:
        """Delete an FCM token for the authenticated user"""
        try:
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            request_data = request.get_json()

            if "fcm_token" not in request_data:
                return jsonify({"error": "Missing required field: fcm_token"}), 400

            account_id = self._get_account_id_from_token()

            params = DeleteFCMTokenParams(user_id=account_id, fcm_token=request_data["fcm_token"])

            result = FCMTokenService.delete_token(params)

            if result.get("success", False):
                return jsonify(result), 200
            else:
                return jsonify(result), 400

        except (AuthorizationHeaderNotFoundError, InvalidAuthorizationHeaderError) as e:
            return jsonify({"success": False, "error": "Authentication failed", "message": str(e)}), 401
        except Exception as e:
            Logger.error(message=f"Error in FCM token DELETE endpoint: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error", "message": str(e)}), 500
