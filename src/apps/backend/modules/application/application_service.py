from flask import Flask

from modules.application.internals.security_headers import SecurityHeaders


class ApplicationService:
    @staticmethod
    def install_security_headers(app: Flask) -> None:
        SecurityHeaders.init_app(app)
