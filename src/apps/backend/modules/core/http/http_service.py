from typing import Optional

from modules.core.http.internal.http_sender import HttpSender
from modules.core.http.types import (
    DEFAULT_TIMEOUT_SECONDS,
    HttpFormBody,
    HttpHeaders,
    HttpJsonBody,
    HttpMethod,
    HttpQueryParams,
    HttpRequest,
    HttpResponse,
)


class HttpService:
    @staticmethod
    def send(*, request: HttpRequest) -> HttpResponse:
        return HttpSender.send(request)

    @staticmethod
    def get(
        *,
        url: str,
        headers: Optional[HttpHeaders] = None,
        query_params: Optional[HttpQueryParams] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        allow_internal_target: bool = False,
    ) -> HttpResponse:
        return HttpSender.send(
            HttpRequest(
                url=url,
                method=HttpMethod.GET,
                headers=headers or {},
                query_params=query_params or {},
                timeout_seconds=timeout_seconds,
                allow_internal_target=allow_internal_target,
            )
        )

    @staticmethod
    def post_json(
        *,
        url: str,
        body: HttpJsonBody,
        headers: Optional[HttpHeaders] = None,
        query_params: Optional[HttpQueryParams] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        allow_internal_target: bool = False,
    ) -> HttpResponse:
        return HttpSender.send(
            HttpRequest(
                url=url,
                method=HttpMethod.POST,
                headers=headers or {},
                query_params=query_params or {},
                json_body=body,
                timeout_seconds=timeout_seconds,
                allow_internal_target=allow_internal_target,
            )
        )

    @staticmethod
    def post_form(
        *,
        url: str,
        body: HttpFormBody,
        headers: Optional[HttpHeaders] = None,
        query_params: Optional[HttpQueryParams] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        allow_internal_target: bool = False,
    ) -> HttpResponse:
        return HttpSender.send(
            HttpRequest(
                url=url,
                method=HttpMethod.POST,
                headers=headers or {},
                query_params=query_params or {},
                form_body=body,
                timeout_seconds=timeout_seconds,
                allow_internal_target=allow_internal_target,
            )
        )
