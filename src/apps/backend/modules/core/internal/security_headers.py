from typing import List

from flask import Flask
from flask.wrappers import Response

from modules.config.config_service import ConfigService


class SecurityHeaders:
    _HSTS_VALUE = "max-age=63072000; includeSubDomains"

    @classmethod
    def init_app(cls, app: Flask) -> None:
        behind_proxy = ConfigService[bool].get_value(key="is_server_running_behind_proxy", default=False)
        csp_value = cls._build_csp()

        @app.after_request
        def _apply_security_headers(response: Response) -> Response:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Content-Security-Policy"] = csp_value
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
            if behind_proxy:
                response.headers["Strict-Transport-Security"] = cls._HSTS_VALUE
            return response

    @classmethod
    def _build_csp(cls) -> str:
        script_src = cls._source_list("'self'", "web.csp_script_src_extra")
        style_src = "'self' 'unsafe-inline'"
        connect_src = cls._source_list("'self'", "web.csp_connect_src_extra")
        return (
            "default-src 'self'; "
            f"script-src {script_src}; "
            f"style-src {style_src}; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            f"connect-src {connect_src}; "
            "worker-src 'self' blob:; "
            "frame-ancestors 'none'"
        )

    @staticmethod
    def _source_list(base: str, config_key: str) -> str:
        extra: List[str] = ConfigService[List[str]].get_value(key=config_key, default=[])
        return " ".join([base, *extra]) if extra else base
