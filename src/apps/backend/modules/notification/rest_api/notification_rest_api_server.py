from flask import Blueprint

from modules.notification.rest_api.notification_router import NotificationRouter


class NotificationRestApiServer:
    """
    Entry point for registering notification REST API endpoints

    Follows the same pattern as other API modules for consistency
    """

    @staticmethod
    def create() -> Blueprint:
        """
        Creates and configures the notification API blueprint

        Returns:
            Blueprint with all notification endpoints registered
        """
        notification_api_blueprint = Blueprint("notification", __name__)
        return NotificationRouter.create_route(blueprint=notification_api_blueprint)
