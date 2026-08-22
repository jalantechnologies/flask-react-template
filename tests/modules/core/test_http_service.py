import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Iterator

import pytest

from modules.core.http.errors import HttpConflictingBodyError, HttpTransportError
from modules.core.http.http_service import HttpService
from modules.core.http.types import DEFAULT_TIMEOUT_SECONDS, HttpMethod, HttpRequest

HTTP_LOGGER = "modules.logger.internal.console_logger"

UNROUTABLE_URL = "http://127.0.0.1:1/private/path"
SECRET_QUERY_PARAM = "access_token=super-secret-token"


class _EchoHandler(BaseHTTPRequestHandler):
    sleep_seconds = 0.0

    def _respond(self, payload: dict[str, object]) -> None:
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        self._respond({"method": "GET", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode()
        self._respond({"method": "POST", "content_type": self.headers.get("Content-Type"), "body": raw_body})

    def log_message(self, *_args: object) -> None:
        return


@pytest.fixture
def echo_server() -> Iterator[str]:
    _EchoHandler.sleep_seconds = 0.0
    server = HTTPServer(("127.0.0.1", 0), _EchoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    try:
        yield f"http://{host!s}:{port}"
    finally:
        server.shutdown()
        thread.join()


class TestGivenAReachableServer:
    class TestWhenSendingAGetRequest:
        def test_then_returns_a_successful_typed_response(self, echo_server: str) -> None:
            response = HttpService.get(url=f"{echo_server}/health", query_params={"probe": "yes"})

            assert response.is_success
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            assert response.json()["method"] == "GET"
            assert response.json()["path"] == "/health?probe=yes"

    class TestWhenPostingAJsonBody:
        def test_then_sends_json_content(self, echo_server: str) -> None:
            response = HttpService.post_json(url=f"{echo_server}/items", body={"name": "widget"})

            assert response.is_success
            assert response.json()["content_type"] == "application/json"
            assert json.loads(response.json()["body"]) == {"name": "widget"}

    class TestWhenPostingAFormBody:
        def test_then_sends_form_encoded_content(self, echo_server: str) -> None:
            response = HttpService.post_form(url=f"{echo_server}/items", body={"name": "widget"})

            assert response.is_success
            assert response.json()["content_type"] == "application/x-www-form-urlencoded"
            assert response.json()["body"] == "name=widget"

    class TestWhenTheServerIsSlowerThanTheTimeout:
        def test_then_raises_a_transport_error(self, echo_server: str) -> None:
            _EchoHandler.sleep_seconds = 1.0

            with pytest.raises(HttpTransportError) as raised:
                HttpService.get(url=f"{echo_server}/slow", timeout_seconds=0.1)

            assert raised.value.http_code == 503
            assert raised.value.reason == "the request timed out"


class TestGivenAnUnreachableServer:
    class TestWhenTheConnectionIsRefused:
        def test_then_raises_a_transport_error_mapping_to_503(self) -> None:
            with pytest.raises(HttpTransportError) as raised:
                HttpService.get(url=UNROUTABLE_URL)

            assert raised.value.http_code == 503
            assert raised.value.host == "127.0.0.1"
            assert raised.value.reason == "the connection could not be established"

    class TestWhenTheFailureIsLogged:
        def test_then_the_log_line_omits_the_url_and_query_string(self, caplog: pytest.LogCaptureFixture) -> None:
            url = f"{UNROUTABLE_URL}?{SECRET_QUERY_PARAM}"

            with caplog.at_level("ERROR", logger=HTTP_LOGGER):
                with pytest.raises(HttpTransportError):
                    HttpService.get(url=url)

            logged = " ".join(record.getMessage() for record in caplog.records)
            assert "host=127.0.0.1" in logged
            assert url not in logged
            assert "/private/path" not in logged
            assert "super-secret-token" not in logged

    class TestWhenTheErrorMessageIsRead:
        def test_then_it_names_only_the_host(self) -> None:
            with pytest.raises(HttpTransportError) as raised:
                HttpService.get(url=f"{UNROUTABLE_URL}?{SECRET_QUERY_PARAM}")

            assert "super-secret-token" not in raised.value.message
            assert "/private/path" not in raised.value.message
            assert "127.0.0.1" in raised.value.message


class TestGivenARequestCarryingBothBodies:
    class TestWhenItIsSent:
        def test_then_it_is_rejected_before_any_call(self, echo_server: str) -> None:
            request = HttpRequest(
                url=f"{echo_server}/items",
                method=HttpMethod.POST,
                json_body={"name": "widget"},
                form_body={"name": "widget"},
            )

            with pytest.raises(HttpConflictingBodyError) as raised:
                HttpService.send(request=request)

            assert raised.value.http_code == 400


class TestGivenARequestWithNoExplicitTimeout:
    class TestWhenItIsBuilt:
        def test_then_it_carries_the_default_timeout(self) -> None:
            assert HttpRequest(url="https://example.com").timeout_seconds == DEFAULT_TIMEOUT_SECONDS
            assert DEFAULT_TIMEOUT_SECONDS == 15.0
