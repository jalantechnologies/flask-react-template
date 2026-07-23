from unittest.mock import MagicMock, patch

from flask import Flask

from modules.application.internals.security_headers import SecurityHeaders

EXPECTED_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)


def _build_client(behind_proxy: bool):
    with patch("modules.application.internals.security_headers.ConfigService") as mock_config_service:
        mock_config_service.__getitem__.return_value.get_value.return_value = behind_proxy
        app = Flask(__name__)

        @app.route("/ping")
        def _ping() -> str:
            return "pong"

        SecurityHeaders.init_app(app)
        return app.test_client()


class TestGivenSecurityHeadersAreApplied:
    class TestWhenNotBehindProxy:
        def test_then_baseline_headers_are_present(self) -> None:
            response = _build_client(behind_proxy=False).get("/ping")

            assert response.headers["X-Content-Type-Options"] == "nosniff"
            assert response.headers["Content-Security-Policy"] == EXPECTED_CSP
            assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
            assert response.headers["Permissions-Policy"] == "geolocation=(), camera=(), microphone=()"

        def test_then_csp_keeps_scripts_strict_and_styles_inline(self) -> None:
            response = _build_client(behind_proxy=False).get("/ping")

            csp = response.headers["Content-Security-Policy"]
            assert "script-src 'self'; " in csp
            assert "'unsafe-inline'" not in csp.split("script-src")[1].split(";")[0]
            assert "style-src 'self' 'unsafe-inline'" in csp

        def test_then_hsts_is_absent(self) -> None:
            response = _build_client(behind_proxy=False).get("/ping")

            assert "Strict-Transport-Security" not in response.headers

    class TestWhenBehindProxy:
        def test_then_hsts_is_present(self) -> None:
            response = _build_client(behind_proxy=True).get("/ping")

            assert response.headers["Strict-Transport-Security"] == "max-age=63072000; includeSubDomains"


class TestGivenProxyFlagIsReadOnce:
    class TestWhenInitAppIsCalled:
        @patch("modules.application.internals.security_headers.ConfigService")
        def test_then_config_is_read_at_startup(self, mock_config_service: MagicMock) -> None:
            mock_config_service.__getitem__.return_value.get_value.return_value = False
            app = Flask(__name__)

            @app.route("/ping")
            def _ping() -> str:
                return "pong"

            SecurityHeaders.init_app(app)
            read_count_after_init = mock_config_service.__getitem__.return_value.get_value.call_count

            client = app.test_client()
            client.get("/ping")
            client.get("/ping")

            assert read_count_after_init == 1
            assert mock_config_service.__getitem__.return_value.get_value.call_count == 1


class TestGivenCorsIsConfigured:
    class TestWhenReadingCorsOrigin:
        @patch("modules.config.config_service.ConfigService.get_value")
        def test_then_origin_reflects_config_and_is_not_wildcard(self, mock_get_value: MagicMock) -> None:
            from modules.config.config_service import ConfigService

            mock_get_value.return_value = "https://app.example.com"
            origin = ConfigService[str].get_value(key="web.cors_allowed_origin", default="http://localhost:3000")

            assert origin == "https://app.example.com"
            assert origin != "*"
