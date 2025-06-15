from datetime import datetime
from typing import Any, Dict

from modules.logger.logger import Logger
from modules.notification.internal.store.fcm_token_model import FCMTokenModel
from modules.notification.internal.store.fcm_token_repository import FCMTokenRepository
from modules.notification.types import AddFCMTokenParams, DeleteFCMTokenParams, FCMToken, GetFCMTokensParams


class FCMTokenService:
    """Service for managing FCM tokens"""

    @staticmethod
    def add_token(params: AddFCMTokenParams) -> Dict[str, Any]:
        """Add a new FCM token for a user"""
        try:
            now = datetime.now()

            existing_token = FCMTokenRepository.collection().find_one(
                {"user_id": params.user_id, "fcm_token": params.fcm_token, "active": True}
            )

            if existing_token:
                return {
                    "success": True,
                    "message": "Token already exists",
                    "token": FCMTokenService._convert_bson_to_fcm_token(existing_token),
                }

            FCMTokenRepository.collection().update_many(
                {"fcm_token": params.fcm_token, "active": True}, {"$set": {"active": False, "updated_at": now}}
            )

            token_model = FCMTokenModel(
                id=None,
                user_id=params.user_id,
                fcm_token=params.fcm_token,
                device_info=params.device_info,
                active=True,
                created_at=now,
                updated_at=now,
            )

            result = FCMTokenRepository.collection().insert_one(token_model.to_bson())
            token_bson = FCMTokenRepository.collection().find_one({"_id": result.inserted_id})

            return {
                "success": True,
                "message": "Token added successfully",
                "token": FCMTokenService._convert_bson_to_fcm_token(token_bson),
            }

        except Exception as e:
            Logger.error(message=f"Error adding FCM token: {str(e)}")
            return {"success": False, "error": "Failed to add token", "message": str(e)}

    @staticmethod
    def get_tokens(params: GetFCMTokensParams) -> Dict[str, Any]:
        """Get all active FCM tokens for a user"""
        try:
            tokens_cursor = (
                FCMTokenRepository.collection().find({"user_id": params.user_id, "active": True}).sort("created_at", -1)
            )

            tokens = [FCMTokenService._convert_bson_to_fcm_token(token_bson) for token_bson in tokens_cursor]

            return {"success": True, "tokens": tokens, "count": len(tokens)}

        except Exception as e:
            Logger.error(message=f"Error getting FCM tokens: {str(e)}")
            return {"success": False, "error": "Failed to get tokens", "message": str(e)}

    @staticmethod
    def delete_token(params: DeleteFCMTokenParams) -> Dict[str, Any]:
        """Delete an FCM token for a user"""
        try:
            result = FCMTokenRepository.collection().update_one(
                {"user_id": params.user_id, "fcm_token": params.fcm_token, "active": True},
                {"$set": {"active": False, "updated_at": datetime.now()}},
            )

            if result.modified_count > 0:
                return {"success": True, "message": "Token deleted successfully"}
            else:
                return {
                    "success": False,
                    "error": "Token not found",
                    "message": "No active token found for the given user and token",
                }

        except Exception as e:
            Logger.error(message=f"Error deleting FCM token: {str(e)}")
            return {"success": False, "error": "Failed to delete token", "message": str(e)}

    @staticmethod
    def _convert_bson_to_fcm_token(token_bson: Dict) -> FCMToken:
        """Convert MongoDB BSON to FCMToken object"""
        return FCMToken(
            id=str(token_bson["_id"]),
            user_id=token_bson["user_id"],
            fcm_token=token_bson["fcm_token"],
            device_info=token_bson.get("device_info"),
            active=token_bson["active"],
            created_at=token_bson["created_at"].isoformat(),
            updated_at=token_bson["updated_at"].isoformat(),
        )
