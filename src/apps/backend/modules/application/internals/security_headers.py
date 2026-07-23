from flask import Flask
from flask.wrappers import Response

from modules.config.config_service import ConfigService


class SecurityHeaders:
    _HSTS_VALUE = "max-age=63072000; includeSubDomains"
    _CSP_VALUE = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )

    @classmethod
    def init_app(cls, app: Flask) -> None:
        behind_proxy = cls._is_behind_proxy()

        @app.after_request
        def _apply_security_headers(response: Response) -> Response:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Content-Security-Policy"] = cls._CSP_VALUE
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
            if behind_proxy:
                response.headers["Strict-Transport-Security"] = cls._HSTS_VALUE
            return response

    @staticmethod
    def _is_behind_proxy() -> bool:
        return ConfigService[bool].get_value(key="is_server_running_behind_proxy", default=False)
