from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import ipaddress
import math
import os
from pathlib import Path
import socket
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from .evidence import content_addressed_ref, verify_content_addressed_ref


class HttpAcquisitionErrorCode(str, Enum):
    INVALID_URL = "INVALID_URL"
    UNSAFE_NETWORK_TARGET = "UNSAFE_NETWORK_TARGET"
    DNS_FAILURE = "DNS_FAILURE"
    REDIRECT_LIMIT = "REDIRECT_LIMIT"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    HTTP_STATUS = "HTTP_STATUS"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    UNSUPPORTED_CONTENT_TYPE = "UNSUPPORTED_CONTENT_TYPE"
    UNSUPPORTED_CONTENT_ENCODING = "UNSUPPORTED_CONTENT_ENCODING"
    RESPONSE_TOO_LARGE = "RESPONSE_TOO_LARGE"
    EMPTY_BODY = "EMPTY_BODY"
    SNAPSHOT_EXISTS = "SNAPSHOT_EXISTS"
    SNAPSHOT_WRITE_ERROR = "SNAPSHOT_WRITE_ERROR"


class HttpAcquisitionError(RuntimeError):
    def __init__(
        self,
        code: HttpAcquisitionErrorCode,
        url: str,
        detail: str,
        *,
        status: int | None = None,
    ) -> None:
        super().__init__(f"{code.value}: {detail}")
        self.code = code
        self.url = url
        self.detail = detail
        self.status = status

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "FAIL",
            "code": self.code.value,
            "url": self.url,
            "httpStatus": self.status,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class DirectHttpPolicy:
    timeout_seconds: float = 15.0
    max_bytes: int = 2_000_000
    max_redirects: int = 5
    allowed_content_types: tuple[str, ...] = (
        "text/html",
        "text/plain",
        "application/json",
        "application/xhtml+xml",
    )
    allowed_schemes: tuple[str, ...] = ("https",)
    allow_private_network: bool = False
    user_agent: str = "Podium7/0.1 direct-http-acquisition"

    def __post_init__(self) -> None:
        if isinstance(self.timeout_seconds, bool) or not isinstance(self.timeout_seconds, (int, float)):
            raise ValueError("timeout_seconds must be a finite positive number")
        if not math.isfinite(float(self.timeout_seconds)) or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a finite positive number")
        if isinstance(self.max_bytes, bool) or not isinstance(self.max_bytes, int) or self.max_bytes < 1:
            raise ValueError("max_bytes must be a positive integer")
        if isinstance(self.max_redirects, bool) or not isinstance(self.max_redirects, int) or self.max_redirects < 0:
            raise ValueError("max_redirects must be a non-negative integer")
        if not self.allowed_content_types:
            raise ValueError("allowed_content_types cannot be empty")
        if any(
            not isinstance(value, str)
            or not value.strip()
            or value != value.strip().lower()
            or "/" not in value
            for value in self.allowed_content_types
        ):
            raise ValueError("allowed_content_types must contain normalized media types")
        if len(set(self.allowed_content_types)) != len(self.allowed_content_types):
            raise ValueError("allowed_content_types cannot contain duplicates")
        if not self.allowed_schemes:
            raise ValueError("allowed_schemes cannot be empty")
        if any(value not in {"http", "https"} for value in self.allowed_schemes):
            raise ValueError("allowed_schemes can contain only http or https")
        if len(set(self.allowed_schemes)) != len(self.allowed_schemes):
            raise ValueError("allowed_schemes cannot contain duplicates")
        if not isinstance(self.allow_private_network, bool):
            raise ValueError("allow_private_network must be boolean")
        if not isinstance(self.user_agent, str) or not self.user_agent.strip():
            raise ValueError("user_agent must be non-empty text")


@dataclass(frozen=True)
class DirectHttpAcquisition:
    requested_url: str
    final_url: str
    redirect_count: int
    status: int
    content_type: str
    charset: str | None
    body: bytes
    sha256: str

    @property
    def size_bytes(self) -> int:
        return len(self.body)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "PASS",
            "requestedUrl": self.requested_url,
            "finalUrl": self.final_url,
            "redirectCount": self.redirect_count,
            "httpStatus": self.status,
            "contentType": self.content_type,
            "charset": self.charset,
            "sizeBytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class FrozenHttpSnapshot:
    acquisition: DirectHttpAcquisition
    snapshot: str
    content_ref: str

    def to_dict(self) -> dict[str, object]:
        payload = self.acquisition.to_dict()
        payload.update({"snapshot": self.snapshot, "contentRef": self.content_ref})
        return payload


def _raise(
    code: HttpAcquisitionErrorCode,
    url: str,
    detail: str,
    *,
    status: int | None = None,
) -> None:
    raise HttpAcquisitionError(code, url, detail, status=status)


def _validate_url(url: str, policy: DirectHttpPolicy) -> None:
    if not isinstance(url, str) or not url.strip() or url != url.strip():
        _raise(HttpAcquisitionErrorCode.INVALID_URL, str(url), "URL must be non-empty text without surrounding whitespace")

    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, f"invalid URL: {exc}")

    scheme = parsed.scheme.lower()
    if scheme not in policy.allowed_schemes:
        _raise(
            HttpAcquisitionErrorCode.INVALID_URL,
            url,
            f"URL scheme {scheme or '<missing>'} is not allowed by the acquisition policy",
        )
    if not parsed.hostname:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, "URL must contain a hostname")
    if parsed.username is not None or parsed.password is not None:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, "credential-bearing URLs are not allowed")
    if parsed.fragment:
        _raise(HttpAcquisitionErrorCode.INVALID_URL, url, "URL fragments are not allowed")

    if policy.allow_private_network:
        return

    target_port = port if port is not None else (443 if scheme == "https" else 80)
    try:
        addresses = socket.getaddrinfo(parsed.hostname, target_port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, f"hostname resolution failed: {exc}")

    if not addresses:
        _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, "hostname resolution returned no addresses")

    observed: set[str] = set()
    for item in addresses:
        raw_address = item[4][0]
        try:
            address = ipaddress.ip_address(raw_address)
        except ValueError:
            _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, f"resolver returned invalid address {raw_address!r}")
        observed.add(address.compressed)
        if not address.is_global:
            _raise(
                HttpAcquisitionErrorCode.UNSAFE_NETWORK_TARGET,
                url,
                f"hostname resolves to non-global address {address.compressed}",
            )

    if not observed:
        _raise(HttpAcquisitionErrorCode.DNS_FAILURE, url, "hostname resolution produced no usable IP addresses")


@dataclass
class _RedirectState:
    count: int = 0


class _PolicyRedirectHandler(HTTPRedirectHandler):
    def __init__(self, policy: DirectHttpPolicy, state: _RedirectState) -> None:
        super().__init__()
        self._policy = policy
        self._state = state

    def http_error_302(self, req, fp, code, msg, headers):  # type: ignore[no-untyped-def]
        location = headers.get("Location") or headers.get("URI")
        if location is not None:
            target = urljoin(req.full_url, location)
            _validate_url(target, self._policy)
        return super().http_error_302(req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        next_count = self._state.count + 1
        if next_count > self._policy.max_redirects:
            _raise(
                HttpAcquisitionErrorCode.REDIRECT_LIMIT,
                req.full_url,
                f"redirect count would exceed limit {self._policy.max_redirects}",
                status=code,
            )
        _validate_url(newurl, self._policy)
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            self._state.count = next_count
        return redirected


def _map_url_error(url: str, exc: URLError) -> HttpAcquisitionError:
    reason = exc.reason
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return HttpAcquisitionError(HttpAcquisitionErrorCode.TIMEOUT, url, f"request timed out: {reason}")
    return HttpAcquisitionError(HttpAcquisitionErrorCode.NETWORK_ERROR, url, f"network request failed: {reason}")


def acquire_http(url: str, policy: DirectHttpPolicy = DirectHttpPolicy()) -> DirectHttpAcquisition:
    _validate_url(url, policy)
    redirect_state = _RedirectState()
    opener = build_opener(ProxyHandler({}), _PolicyRedirectHandler(policy, redirect_state))
    request = Request(
        url,
        method="GET",
        headers={
            "User-Agent": policy.user_agent,
            "Accept-Encoding": "identity",
            "Accept": ", ".join(policy.allowed_content_types),
        },
    )

    try:
        with opener.open(request, timeout=float(policy.timeout_seconds)) as response:
            final_url = response.geturl()
            _validate_url(final_url, policy)
            status = int(response.getcode())
            if status < 200 or status >= 300:
                _raise(
                    HttpAcquisitionErrorCode.HTTP_STATUS,
                    final_url,
                    f"unexpected HTTP status {status}",
                    status=status,
                )

            raw_content_type = response.headers.get("Content-Type")
            if not raw_content_type:
                _raise(
                    HttpAcquisitionErrorCode.MALFORMED_RESPONSE,
                    final_url,
                    "response is missing Content-Type",
                    status=status,
                )
            content_type = response.headers.get_content_type().lower()
            if content_type not in policy.allowed_content_types:
                _raise(
                    HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_TYPE,
                    final_url,
                    f"content type {content_type!r} is not allowed",
                    status=status,
                )

            content_encoding = response.headers.get("Content-Encoding")
            if content_encoding is not None and content_encoding.strip().lower() not in {"", "identity"}:
                _raise(
                    HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_ENCODING,
                    final_url,
                    f"content encoding {content_encoding!r} is not supported",
                    status=status,
                )

            raw_length = response.headers.get("Content-Length")
            if raw_length is not None:
                try:
                    declared_length = int(raw_length)
                except ValueError:
                    _raise(
                        HttpAcquisitionErrorCode.MALFORMED_RESPONSE,
                        final_url,
                        f"invalid Content-Length {raw_length!r}",
                        status=status,
                    )
                if declared_length < 0:
                    _raise(
                        HttpAcquisitionErrorCode.MALFORMED_RESPONSE,
                        final_url,
                        f"invalid negative Content-Length {declared_length}",
                        status=status,
                    )
                if declared_length > policy.max_bytes:
                    _raise(
                        HttpAcquisitionErrorCode.RESPONSE_TOO_LARGE,
                        final_url,
                        f"declared response size {declared_length} exceeds limit {policy.max_bytes}",
                        status=status,
                    )

            body = response.read(policy.max_bytes + 1)
            if len(body) > policy.max_bytes:
                _raise(
                    HttpAcquisitionErrorCode.RESPONSE_TOO_LARGE,
                    final_url,
                    f"response body exceeds limit {policy.max_bytes}",
                    status=status,
                )
            if not body:
                _raise(HttpAcquisitionErrorCode.EMPTY_BODY, final_url, "response body is empty", status=status)

            charset = response.headers.get_content_charset()
            digest = hashlib.sha256(body).hexdigest()
            return DirectHttpAcquisition(
                requested_url=url,
                final_url=final_url,
                redirect_count=redirect_state.count,
                status=status,
                content_type=content_type,
                charset=charset,
                body=body,
                sha256=digest,
            )
    except HttpAcquisitionError:
        raise
    except HTTPError as exc:
        raise HttpAcquisitionError(
            HttpAcquisitionErrorCode.HTTP_STATUS,
            exc.geturl() or url,
            f"unexpected HTTP status {exc.code}",
            status=exc.code,
        ) from exc
    except URLError as exc:
        raise _map_url_error(url, exc) from exc
    except (socket.timeout, TimeoutError) as exc:
        raise HttpAcquisitionError(
            HttpAcquisitionErrorCode.TIMEOUT,
            url,
            f"request timed out: {exc}",
        ) from exc
    except OSError as exc:
        raise HttpAcquisitionError(
            HttpAcquisitionErrorCode.NETWORK_ERROR,
            url,
            f"network request failed: {exc}",
        ) from exc


def freeze_http_snapshot(
    acquisition: DirectHttpAcquisition,
    destination: str | Path,
    *,
    overwrite: bool = False,
) -> FrozenHttpSnapshot:
    path = Path(destination)
    if not path.name:
        _raise(HttpAcquisitionErrorCode.SNAPSHOT_WRITE_ERROR, acquisition.final_url, "snapshot destination must name a file")
    if path.exists() and not overwrite:
        _raise(
            HttpAcquisitionErrorCode.SNAPSHOT_EXISTS,
            acquisition.final_url,
            f"snapshot already exists: {path}",
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary_path = Path(handle.name)
            handle.write(acquisition.body)
            handle.flush()
            os.fsync(handle.fileno())

        if overwrite:
            os.replace(temporary_path, path)
            temporary_path = None
        else:
            try:
                os.link(temporary_path, path)
            except FileExistsError:
                _raise(
                    HttpAcquisitionErrorCode.SNAPSHOT_EXISTS,
                    acquisition.final_url,
                    f"snapshot already exists: {path}",
                )
            temporary_path.unlink()
            temporary_path = None

        observed_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed_digest != acquisition.sha256:
            _raise(
                HttpAcquisitionErrorCode.SNAPSHOT_WRITE_ERROR,
                acquisition.final_url,
                f"snapshot digest mismatch after write: expected {acquisition.sha256}, observed {observed_digest}",
            )
        reference = content_addressed_ref(path)
        if not verify_content_addressed_ref(reference):
            _raise(
                HttpAcquisitionErrorCode.SNAPSHOT_WRITE_ERROR,
                acquisition.final_url,
                "written snapshot content reference failed verification",
            )
        return FrozenHttpSnapshot(acquisition=acquisition, snapshot=str(path), content_ref=reference)
    except HttpAcquisitionError:
        raise
    except OSError as exc:
        raise HttpAcquisitionError(
            HttpAcquisitionErrorCode.SNAPSHOT_WRITE_ERROR,
            acquisition.final_url,
            f"snapshot write failed: {exc}",
        ) from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


def acquire_and_freeze_http(
    url: str,
    destination: str | Path,
    policy: DirectHttpPolicy = DirectHttpPolicy(),
    *,
    overwrite: bool = False,
) -> FrozenHttpSnapshot:
    acquisition = acquire_http(url, policy)
    return freeze_http_snapshot(acquisition, destination, overwrite=overwrite)


__all__ = [
    "DirectHttpAcquisition",
    "DirectHttpPolicy",
    "FrozenHttpSnapshot",
    "HttpAcquisitionError",
    "HttpAcquisitionErrorCode",
    "acquire_and_freeze_http",
    "acquire_http",
    "freeze_http_snapshot",
]
