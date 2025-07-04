from flask import Blueprint

from modules.notification.rest_api.notification_router import NotificationRouter


class NotificationRestApiServer:
    @staticmethod
    def create() -> Blueprint:
        notification_api_blueprint = Blueprint("notification", __name__)
        return NotificationRouter.create_route(blueprint=notification_api_blueprint)
