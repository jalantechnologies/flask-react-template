import requests

from modules.core.http.errors import HttpConflictingBodyError, HttpTransportError
from modules.core.http.types import HttpRequest, HttpResponse
from modules.logger.logger import Logger


class HttpSender:
    @staticmethod
    def send(request: HttpRequest) -> HttpResponse:
        if request.has_conflicting_body:
            raise HttpConflictingBodyError()

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
        except requests.RequestException as err:
            raise HttpSender._as_transport_error(request, err) from err

        return HttpResponse(status_code=response.status_code, headers=dict(response.headers), body=response.text)

    @staticmethod
    def _as_transport_error(request: HttpRequest, err: requests.RequestException) -> HttpTransportError:
        reason = HttpSender._describe_failure(err)
        Logger.error(
            message=(
                "[core.http.transport_failure] Outbound HTTP call failed | "
                f"host={request.host} method={request.method.value} reason={reason}"
            )
        )
        return HttpTransportError(host=request.host, reason=reason, original_error=err)

    @staticmethod
    def _describe_failure(err: requests.RequestException) -> str:
        if isinstance(err, requests.Timeout):
            return "the request timed out"
        if isinstance(err, requests.ConnectionError):
            return "the connection could not be established"
        return "the transport failed"
