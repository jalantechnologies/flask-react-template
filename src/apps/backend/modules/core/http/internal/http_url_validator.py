import ipaddress
import socket
from typing import Optional, Union

from modules.core.http.errors import HttpBlockedTargetError, HttpUnsupportedSchemeError
from modules.core.http.types import ALLOWED_SCHEMES, UNKNOWN_HOST, HttpRequest

type IpAddress = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class HttpUrlValidator:
    @staticmethod
    def validate(request: HttpRequest) -> None:
        scheme = request.scheme
        if scheme not in ALLOWED_SCHEMES:
            raise HttpUnsupportedSchemeError(scheme=scheme or "none")

        host = request.host
        if not host or host == UNKNOWN_HOST:
            raise HttpBlockedTargetError(host=host or "none", reason="the URL carries no host")

        if request.allow_internal_target:
            return

        for address in HttpUrlValidator._resolve(host):
            if HttpUrlValidator._is_internal(address):
                raise HttpBlockedTargetError(host=host, reason="the host resolves to an internal address")

    @staticmethod
    def _resolve(host: str) -> list[IpAddress]:
        literal = HttpUrlValidator._as_literal(host)
        if literal is not None:
            return [literal]

        try:
            resolved = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        except socket.gaierror as err:
            raise HttpBlockedTargetError(host=host, reason="the host could not be resolved") from err

        addresses = [HttpUrlValidator._as_literal(str(entry[4][0])) for entry in resolved]
        return [address for address in addresses if address is not None]

    @staticmethod
    def _as_literal(value: str) -> Optional[IpAddress]:
        candidate = value.strip("[]").split("%")[0]
        try:
            return ipaddress.ip_address(candidate)
        except ValueError:
            return None

    @staticmethod
    def _is_internal(address: IpAddress) -> bool:
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
            return HttpUrlValidator._is_internal(address.ipv4_mapped)

        return (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
        )
