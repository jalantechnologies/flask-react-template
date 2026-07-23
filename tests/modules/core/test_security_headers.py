from typing import Dict, List, Optional
from unittest.mock import MagicMock, patch

from flask import Flask
from flask.testing import FlaskClient

from modules.core.security_headers import SecurityHeaders

STRICT_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none'"
)


def _build_client(*, behind_proxy: bool = False, config_overrides: Optional[Dict[str, object]] = None) -> FlaskClient:
    overrides = config_overrides or {}

    def _fake_get_value(key: str, default: object = None) -> object:
        if key == "is_server_running_behind_proxy":
            return behind_proxy
        return overrides.get(key, default)

    with patch("modules.core.security_headers.ConfigService") as mock_config_service:
        mock_config_service.__getitem__.return_value.get_value.side_effect = _fake_get_value
        app = Flask(__name__)

        @app.route("/ping")
        def _ping() -> str:
            return "pong"

        SecurityHeaders.init_app(app)
        return app.test_client()


class TestGivenSecurityHeadersAreApplied:
    class TestWhenNotBehindProxy:
        def test_then_baseline_headers_are_present(self) -> None:
            response = _build_client().get("/ping")

            assert response.headers["X-Content-Type-Options"] == "nosniff"
            assert response.headers["Content-Security-Policy"] == STRICT_CSP
            assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
            assert response.headers["Permissions-Policy"] == "geolocation=(), camera=(), microphone=()"

        def test_then_csp_keeps_scripts_strict_and_styles_inline(self) -> None:
            csp = _build_client().get("/ping").headers["Content-Security-Policy"]

            assert "script-src 'self';" in csp
            assert "'unsafe-inline'" not in csp.split("script-src")[1].split(";")[0]
            assert "style-src 'self' 'unsafe-inline'" in csp

        def test_then_hsts_is_absent(self) -> None:
            response = _build_client(behind_proxy=False).get("/ping")

            assert "Strict-Transport-Security" not in response.headers

    class TestWhenBehindProxy:
        def test_then_hsts_is_present(self) -> None:
            response = _build_client(behind_proxy=True).get("/ping")

            assert response.headers["Strict-Transport-Security"] == "max-age=63072000; includeSubDomains"


class TestGivenObservabilityOriginsAreAllowlisted:
    class TestWhenExtraCspSourcesAreConfigured:
        def test_then_connect_and_script_src_include_them(self) -> None:
            overrides: Dict[str, object] = {
                "web.csp_script_src_extra": ["https://cdn.inspectlet.com"],
                "web.csp_connect_src_extra": ["https://*.datadoghq.com", "https://*.inspectlet.com"],
            }
            csp = _build_client(config_overrides=overrides).get("/ping").headers["Content-Security-Policy"]

            assert "script-src 'self' https://cdn.inspectlet.com;" in csp
            assert "connect-src 'self' https://*.datadoghq.com https://*.inspectlet.com;" in csp

        def test_then_styles_and_defaults_stay_unchanged(self) -> None:
            overrides: Dict[str, object] = {"web.csp_connect_src_extra": ["https://*.datadoghq.com"]}
            csp = _build_client(config_overrides=overrides).get("/ping").headers["Content-Security-Policy"]

            assert "default-src 'self';" in csp
            assert "style-src 'self' 'unsafe-inline'" in csp
            assert "frame-ancestors 'none'" in csp

        def test_then_blob_workers_are_allowed_for_session_replay(self) -> None:
            csp = _build_client().get("/ping").headers["Content-Security-Policy"]

            assert "worker-src 'self' blob:;" in csp


class TestGivenProxyFlagIsReadOnce:
    class TestWhenInitAppIsCalled:
        def test_then_config_is_not_reread_per_request(self) -> None:
            calls: List[str] = []

            def _fake_get_value(key: str, default: object = None) -> object:
                calls.append(key)
                if key == "is_server_running_behind_proxy":
                    return False
                return default

            with patch("modules.core.security_headers.ConfigService") as mock_config_service:
                mock_config_service.__getitem__.return_value.get_value.side_effect = _fake_get_value
                app = Flask(__name__)

                @app.route("/ping")
                def _ping() -> str:
                    return "pong"

                SecurityHeaders.init_app(app)
                calls_after_init = list(calls)

                client = app.test_client()
                client.get("/ping")
                client.get("/ping")

            assert "is_server_running_behind_proxy" in calls_after_init
            assert calls == calls_after_init


class TestGivenCorsIsConfigured:
    class TestWhenReadingCorsOrigin:
        @patch("modules.config.config_service.ConfigService.get_value")
        def test_then_origin_reflects_config_and_is_not_wildcard(self, mock_get_value: MagicMock) -> None:
            from modules.config.config_service import ConfigService

            mock_get_value.return_value = "https://app.example.com"
            origin = ConfigService[str].get_value(key="web.cors_allowed_origin", default="http://localhost:3000")

            assert origin == "https://app.example.com"
            assert origin != "*"
