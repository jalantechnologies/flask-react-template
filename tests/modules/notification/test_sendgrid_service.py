import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Iterator, Optional

import pytest
import sendgrid
from python_http_client.exceptions import HTTPError

from modules.notification.errors import EmailRejectedError, EmailServiceUnavailableError
from modules.notification.internal.sendgrid_service import SendGridService
from modules.notification.types import EmailRecipient, EmailSender, NotificationErrorCode, SendEmailParams

UNROUTABLE_HOST = "http://127.0.0.1:1"
NOTIFICATION_LOGGER = "modules.logger.internal.console_logger"

SEND_EMAIL_PARAMS = SendEmailParams(
    recipient=EmailRecipient(email="recipient@example.com"),
    sender=EmailSender(email="sender@example.com", name="Sender"),
    template_id="template-id",
    template_data={"first_name": "first_name"},
)


class _SendGridHandler(BaseHTTPRequestHandler):
    status_code = 202
    sleep_seconds = 0.0

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        body = b'{"errors": [{"message": "simulated"}]}'
        self.send_response(self.status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args: object) -> None:
        return


@pytest.fixture
def sendgrid_server() -> Iterator[str]:
    _SendGridHandler.status_code = 202
    _SendGridHandler.sleep_seconds = 0.0
    server = HTTPServer(("127.0.0.1", 0), _SendGridHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    try:
        yield f"http://{host!s}:{port}"
    finally:
        server.shutdown()
        thread.join()


def _point_sendgrid_at(monkeypatch: pytest.MonkeyPatch, host: str, timeout_seconds: Optional[float] = None) -> None:
    client = sendgrid.SendGridAPIClient(api_key="test-api-key", host=host)
    client.client.timeout = timeout_seconds
    monkeypatch.setattr(SendGridService, "get_client", staticmethod(lambda: client))


class TestGivenTheProviderRejectsTheMessage:
    class TestWhenItRespondsWith400:
        def test_then_raises_the_modules_rejected_error(
            self, sendgrid_server: str, monkeypatch: pytest.MonkeyPatch
        ) -> None:
            _SendGridHandler.status_code = 400
            _point_sendgrid_at(monkeypatch, sendgrid_server)

            with pytest.raises(EmailRejectedError) as raised:
                SendGridService.send_email(SEND_EMAIL_PARAMS)

            assert raised.value.http_code == 502
            assert raised.value.code == NotificationErrorCode.EMAIL_REJECTED
            assert raised.value.status_code == 400
            assert raised.value.recipient == "recipient@example.com"
            assert isinstance(raised.value.__cause__, HTTPError)

    class TestWhenItRespondsWith401:
        def test_then_raises_the_modules_rejected_error(
            self, sendgrid_server: str, monkeypatch: pytest.MonkeyPatch
        ) -> None:
            _SendGridHandler.status_code = 401
            _point_sendgrid_at(monkeypatch, sendgrid_server)

            with pytest.raises(EmailRejectedError) as raised:
                SendGridService.send_email(SEND_EMAIL_PARAMS)

            assert raised.value.status_code == 401

    class TestWhenTheFailureIsLogged:
        def test_then_the_log_line_names_the_error_code(
            self, sendgrid_server: str, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
        ) -> None:
            _SendGridHandler.status_code = 400
            _point_sendgrid_at(monkeypatch, sendgrid_server)

            with caplog.at_level("ERROR", logger=NOTIFICATION_LOGGER):
                with pytest.raises(EmailRejectedError):
                    SendGridService.send_email(SEND_EMAIL_PARAMS)

            logged = " ".join(record.getMessage() for record in caplog.records)
            assert f"notification_error_code={NotificationErrorCode.EMAIL_REJECTED}" in logged
            assert "template_id=template-id" in logged


class TestGivenTheProviderIsFailing:
    class TestWhenItRespondsWith500:
        def test_then_raises_the_modules_unavailable_error(
            self, sendgrid_server: str, monkeypatch: pytest.MonkeyPatch
        ) -> None:
            _SendGridHandler.status_code = 500
            _point_sendgrid_at(monkeypatch, sendgrid_server)

            with pytest.raises(EmailServiceUnavailableError) as raised:
                SendGridService.send_email(SEND_EMAIL_PARAMS)

            assert raised.value.http_code == 503
            assert raised.value.code == NotificationErrorCode.EMAIL_SERVICE_UNAVAILABLE
            assert raised.value.status_code == 500

    class TestWhenItRespondsWith503:
        def test_then_raises_the_modules_unavailable_error(
            self, sendgrid_server: str, monkeypatch: pytest.MonkeyPatch
        ) -> None:
            _SendGridHandler.status_code = 503
            _point_sendgrid_at(monkeypatch, sendgrid_server)

            with pytest.raises(EmailServiceUnavailableError) as raised:
                SendGridService.send_email(SEND_EMAIL_PARAMS)

            assert raised.value.status_code == 503


class TestGivenTheProviderIsUnreachable:
    class TestWhenTheConnectionIsRefused:
        def test_then_raises_the_modules_unavailable_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
            _point_sendgrid_at(monkeypatch, UNROUTABLE_HOST)

            with pytest.raises(EmailServiceUnavailableError) as raised:
                SendGridService.send_email(SEND_EMAIL_PARAMS)

            assert raised.value.http_code == 503
            assert raised.value.status_code is None
            assert isinstance(raised.value.__cause__, OSError)

    class TestWhenTheRequestTimesOut:
        def test_then_raises_the_modules_unavailable_error(
            self, sendgrid_server: str, monkeypatch: pytest.MonkeyPatch
        ) -> None:
            _SendGridHandler.sleep_seconds = 1.0
            _point_sendgrid_at(monkeypatch, sendgrid_server, timeout_seconds=0.1)

            with pytest.raises(EmailServiceUnavailableError) as raised:
                SendGridService.send_email(SEND_EMAIL_PARAMS)

            assert raised.value.http_code == 503
            assert raised.value.code == NotificationErrorCode.EMAIL_SERVICE_UNAVAILABLE
            assert raised.value.status_code is None
            assert isinstance(raised.value.__cause__, TimeoutError)


class TestGivenTheProviderSucceeds:
    class TestWhenItRespondsWith202:
        def test_then_no_error_is_raised(self, sendgrid_server: str, monkeypatch: pytest.MonkeyPatch) -> None:
            _point_sendgrid_at(monkeypatch, sendgrid_server)

            SendGridService.send_email(SEND_EMAIL_PARAMS)
