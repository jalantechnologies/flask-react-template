import requests

from modules.core.errors import AppError
from modules.core.http.errors import HttpConflictingBodyError, HttpTransportError
from modules.core.http.internal.http_url_validator import HttpUrlValidator
from modules.core.http.types import HttpRequest, HttpResponse
from modules.core.logger.logger import Logger


class HttpSender:
    @staticmethod
    def send(request: HttpRequest) -> HttpResponse:
        if request.has_conflicting_body:
            raise HttpConflictingBodyError()

        HttpUrlValidator.validate(request)

        try:
            response = requests.request(
                method=request.method.value,
                url=request.url,
                headers=request.headers,
                params=request.query_params,
                json=request.json_body,
                data=request.form_body,
                timeout=request.timeout_seconds,
                allow_redirects=request.allow_redirects,
            )
        except AppError:
            raise
        except Exception as err:
            raise HttpSender._as_transport_error(request, err) from err

        return HttpResponse(status_code=response.status_code, headers=dict(response.headers), body=response.text)

    @staticmethod
    def _as_transport_error(request: HttpRequest, err: Exception) -> HttpTransportError:
        reason = HttpSender._describe_failure(err)
        Logger.error(
            message=(
                "[core.http.transport_failure] Outbound HTTP call failed | "
                f"host={request.host} method={request.method.value} reason={reason}"
            )
        )
        return HttpTransportError(host=request.host, reason=reason, original_error=err)

    @staticmethod
    def _describe_failure(err: Exception) -> str:
        if isinstance(err, requests.Timeout):
            return "the request timed out"
        if isinstance(err, requests.ConnectionError):
            return "the connection could not be established"
        if isinstance(err, (ValueError, TypeError)):
            return "the request could not be built"
        return "the transport failed"
