from __future__ import annotations

from dataclasses import dataclass
import hashlib
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urljoin, urlsplit

from .http_acquisition import (
    DirectHttpAcquisition,
    DirectHttpPolicy,
    HttpAcquisitionError,
    HttpAcquisitionErrorCode,
)


_REDIRECT_STATUSES = {301, 302, 303, 307, 308}


@dataclass(frozen=True)
class BoundNetworkTarget:
    scheme: str
    host: str
    port: int
    addresses: tuple[str, ...]


def _raise(
    code: HttpAcquisitionErrorCode,
    url: str,
    detail: str,
    *,
    status: int | None = None,
) -> None:
    raise HttpAcquisitionError(code, url, detail, status=status)


def resolve_bound_target(url: str, policy: DirectHttpPolicy) -> BoundNetworkTarget:
    if not isinstance(url, str) or not url.strip() or url != url.strip():
        _raise(HttpAcquisitionErrorCode.INVALID_URL, str(url), "URL must be non-empty text without surrounding whitespace")
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, f"invalid URL: {exc}")

    scheme = parsed.scheme.lower()
    if scheme not in policy.allowed_schemes:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, f"URL scheme {scheme or '<missing>'} is not allowed by the acquisition policy")
    if not parsed.hostname:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, "URL must contain a hostname")
    if parsed.username is not None or parsed.password is not None:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, "credential-bearing URLs are not allowed")
    if parsed.fragment:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, "URL fragments are not allowed")

    target_port = port if port is not None else (443 if scheme == "https" else 80)
    try:
        resolved = socket.getaddrinfo(parsed.hostname, target_port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, f"hostname resolution failed: {exc}")
    if not resolved:
        _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, "hostname resolution returned no addresses")

    addresses: list[str] = []
    for item in resolved:
        raw = item[4][0]
        try:
            address = ipaddress.ip_address(raw)
        except ValueError:
            _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, f"resolver returned invalid address {raw!r}")
        normalized = address.compressed
        if not policy.allow_private_network and not address.is_global:
            _raise(HttpAcquisitionErrorCode.UNSAFE_NETWORK_TARGET, url, f"hostname resolves to non-global address {normalized}")
        if normalized not in addresses:
            addresses.append(normalized)
    if not addresses:
        _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, "hostname resolution produced no usable IP addresses")
    return BoundNetworkTarget(scheme, parsed.hostname, target_port, tuple(addresses))


def _connect(target: BoundNetworkTarget, timeout: float) -> tuple[http.client.HTTPConnection, str]:
    last_error: OSError | None = None
    for address in target.addresses:
        raw_socket: socket.socket | None = None
        try:
            raw_socket = socket.create_connection((address, target.port), timeout=timeout)
            if target.scheme == "https":
                context = ssl.create_default_context()
                wrapped = context.wrap_socket(raw_socket, server_hostname=target.host)
                connection = http.client.HTTPSConnection(target.host, target.port, timeout=timeout, context=context)
                connection.sock = wrapped
            else:
                connection = http.client.HTTPConnection(target.host, target.port, timeout=timeout)
                connection.sock = raw_socket
            return connection, address
        except OSError as exc:
            last_error = exc
            if raw_socket is not None:
                try:
                    raw_socket.close()
                except OSError:
                    pass
    if last_error is None:
        raise OSError("no validated target address available")
    raise last_error


def _request_path(url: str) -> str:
    parsed = urlsplit(url)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return path


def _host_header(target: BoundNetworkTarget) -> str:
    try:
        literal = ipaddress.ip_address(target.host)
    except ValueError:
        authority_host = target.host
    else:
        authority_host = f"[{target.host}]" if literal.version == 6 else target.host
    default_port = 443 if target.scheme == "https" else 80
    if target.port == default_port:
        return authority_host
    return f"{authority_host}:{target.port}"


def acquire_bound_http(url: str, policy: DirectHttpPolicy = DirectHttpPolicy()) -> DirectHttpAcquisition:
    requested_url = url
    current_url = url
    redirect_count = 0

    while True:
        target = resolve_bound_target(current_url, policy)
        connection: http.client.HTTPConnection | None = None
        try:
            connection, _ = _connect(target, float(policy.timeout_seconds))
            connection.request(
                "GET",
                _request_path(current_url),
                headers={
                    "Host": _host_header(target),
                    "User-Agent": policy.user_agent,
                    "Accept-Encoding": "identity",
                    "Accept": ", ".join(policy.allowed_content_types),
                    "Connection": "close",
                },
            )
            response = connection.getresponse()
            status = int(response.status)

            if status in _REDIRECT_STATUSES:
                location = response.getheader("Location") or response.getheader("URI")
                if not location:
                    _raise(HttpAcquisitionErrorCode.MALFORMED_RESPONSE, current_url, "redirect response is missing Location", status=status)
                redirect_count += 1
                if redirect_count > policy.max_redirects:
                    _raise(HttpAcquisitionErrorCode.REDIRECT_LIMIT, current_url, f"redirect count would exceed limit {policy.max_redirects}", status=status)
                current_url = urljoin(current_url, location)
                continue

            if status < 200 or status >= 300:
                _raise(HttpAcquisitionErrorCode.HTTP_STATUS, current_url, f"unexpected HTTP status {status}", status=status)

            raw_content_type = response.getheader("Content-Type")
            if not raw_content_type:
                _raise(HttpAcquisitionErrorCode.MALFORMED_RESPONSE, current_url, "response is missing Content-Type", status=status)
            content_type = response.headers.get_content_type().lower()
            if content_type not in policy.allowed_content_types:
                _raise(HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_TYPE, current_url, f"content type {content_type!r} is not allowed", status=status)

            content_encoding = response.getheader("Content-Encoding")
            if content_encoding is not None and content_encoding.strip().lower() not in {"", "identity"}:
                _raise(HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_ENCODING, current_url, f"content encoding {content_encoding!r} is not supported", status=status)

            raw_length = response.getheader("Content-Length")
            if raw_length is not None:
                try:
                    declared_length = int(raw_length)
                except ValueError:
                    _raise(HttpAcquisitionErrorCode.MALFORMED_RESPONSE, current_url, f"invalid Content-Length {raw_length!r}", status=status)
                if declared_length < 0:
                    _raise(HttpAcquisitionErrorCode.MALFORMED_RESPONSE, current_url, f"invalid negative Content-Length {declared_length}", status=status)
                if declared_length > policy.max_bytes:
                    _raise(HttpAcquisitionErrorCode.RESPONSE_TOO_LARGE, current_url, f"declared response size {declared_length} exceeds limit {policy.max_bytes}", status=status)

            body = response.read(policy.max_bytes + 1)
            if len(body) > policy.max_bytes:
                _raise(HttpAcquisitionErrorCode.RESPONSE_TOO_LARGE, current_url, f"response body exceeds limit {policy.max_bytes}", status=status)
            if not body:
                _raise(HttpAcquisitionErrorCode.EMPTY_BODY, current_url, "response body is empty", status=status)

            return DirectHttpAcquisition(
                requested_url=requested_url,
                final_url=current_url,
                redirect_count=redirect_count,
                status=status,
                content_type=content_type,
                charset=response.headers.get_content_charset(),
                body=body,
                sha256=hashlib.sha256(body).hexdigest(),
            )
        except HttpAcquisitionError:
            raise
        except (socket.timeout, TimeoutError) as exc:
            raise HttpAcquisitionError(HttpAcquisitionErrorCode.TIMEOUT, current_url, f"request timed out: {exc}") from exc
        except ssl.SSLError as exc:
            raise HttpAcquisitionError(HttpAcquisitionErrorCode.NETWORK_ERROR, current_url, f"TLS request failed: {exc}") from exc
        except OSError as exc:
            raise HttpAcquisitionError(HttpAcquisitionErrorCode.NETWORK_ERROR, current_url, f"network request failed: {exc}") from exc
        finally:
            if connection is not None:
                try:
                    connection.close()
                except OSError:
                    pass


__all__ = ["BoundNetworkTarget", "acquire_bound_http", "resolve_bound_target"]
