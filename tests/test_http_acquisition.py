from __future__ import annotations

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import time
import unittest

from podium7.evidence import verify_content_addressed_ref
from podium7.http_acquisition import (
    DirectHttpPolicy,
    HttpAcquisitionError,
    HttpAcquisitionErrorCode,
    acquire_and_freeze_http,
    acquire_http,
    freeze_http_snapshot,
)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):  # type: ignore[no-untyped-def]
        return

    def _send(self, status: int, body: bytes, *, content_type: str | None = "text/plain; charset=utf-8", headers=None) -> None:
        self.send_response(status)
        if content_type is not None:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if body:
            try:
                self.wfile.write(body)
            except BrokenPipeError:
                pass

    def do_GET(self) -> None:
        if self.path == "/ok":
            body = f"accept-encoding={self.headers.get('Accept-Encoding')}".encode("utf-8")
            self._send(200, body)
            return
        if self.path == "/json":
            self._send(200, b'{"ok":true}', content_type="application/json; charset=utf-8")
            return
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path == "/redirect-file":
            self.send_response(302)
            self.send_header("Location", "file:///tmp/not-allowed")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path == "/loop":
            self.send_response(302)
            self.send_header("Location", "/loop")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path == "/error":
            self._send(503, b"unavailable")
            return
        if self.path == "/binary":
            self._send(200, b"abc", content_type="application/octet-stream")
            return
        if self.path == "/gzip":
            self._send(200, b"not-really-gzip", headers={"Content-Encoding": "gzip"})
            return
        if self.path == "/empty":
            self._send(200, b"")
            return
        if self.path == "/large":
            self._send(200, b"x" * 64)
            return
        if self.path == "/large-no-length":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
            self.wfile.write(b"x" * 64)
            return
        if self.path == "/no-content-type":
            self._send(200, b"abc", content_type=None)
            return
        if self.path == "/bad-length":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", "wat")
            self.end_headers()
            return
        if self.path == "/slow":
            time.sleep(0.20)
            self._send(200, b"late")
            return
        self._send(404, b"not found")


class DirectHttpAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def policy(self, **overrides) -> DirectHttpPolicy:
        values = {
            "timeout_seconds": 1.0,
            "max_bytes": 1024,
            "max_redirects": 3,
            "allowed_schemes": ("http",),
            "allow_private_network": True,
        }
        values.update(overrides)
        return DirectHttpPolicy(**values)

    def assert_error(self, code: HttpAcquisitionErrorCode, callback) -> HttpAcquisitionError:
        with self.assertRaises(HttpAcquisitionError) as caught:
            callback()
        self.assertEqual(code, caught.exception.code)
        return caught.exception

    def test_default_policy_is_https_only(self) -> None:
        error = self.assert_error(
            HttpAcquisitionErrorCode.INVALID_URL,
            lambda: acquire_http(f"{self.base_url}/ok"),
        )
        self.assertIn("scheme http", error.detail)

    def test_default_policy_blocks_loopback_before_transport(self) -> None:
        error = self.assert_error(
            HttpAcquisitionErrorCode.UNSAFE_NETWORK_TARGET,
            lambda: acquire_http("https://127.0.0.1/example"),
        )
        self.assertIn("non-global address 127.0.0.1", error.detail)

    def test_success_preserves_bytes_and_response_metadata(self) -> None:
        result = acquire_http(f"{self.base_url}/ok", self.policy())
        self.assertEqual(200, result.status)
        self.assertEqual("text/plain", result.content_type)
        self.assertEqual("utf-8", result.charset)
        self.assertEqual(0, result.redirect_count)
        self.assertEqual(result.requested_url, result.final_url)
        self.assertEqual(b"accept-encoding=identity", result.body)
        self.assertEqual(hashlib.sha256(result.body).hexdigest(), result.sha256)
        self.assertEqual(len(result.body), result.size_bytes)

    def test_declared_redirect_is_followed_and_counted(self) -> None:
        result = acquire_http(f"{self.base_url}/redirect", self.policy())
        self.assertEqual(1, result.redirect_count)
        self.assertEqual(f"{self.base_url}/ok", result.final_url)
        self.assertEqual(b"accept-encoding=identity", result.body)

    def test_redirect_target_is_revalidated(self) -> None:
        error = self.assert_error(
            HttpAcquisitionErrorCode.INVALID_URL,
            lambda: acquire_http(f"{self.base_url}/redirect-file", self.policy()),
        )
        self.assertIn("scheme file", error.detail)

    def test_redirect_limit_fails_explicitly(self) -> None:
        error = self.assert_error(
            HttpAcquisitionErrorCode.REDIRECT_LIMIT,
            lambda: acquire_http(f"{self.base_url}/loop", self.policy(max_redirects=2)),
        )
        self.assertIn("limit 2", error.detail)

    def test_http_error_status_fails_explicitly(self) -> None:
        error = self.assert_error(
            HttpAcquisitionErrorCode.HTTP_STATUS,
            lambda: acquire_http(f"{self.base_url}/error", self.policy()),
        )
        self.assertEqual(503, error.status)

    def test_unsupported_content_type_fails_explicitly(self) -> None:
        self.assert_error(
            HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_TYPE,
            lambda: acquire_http(f"{self.base_url}/binary", self.policy()),
        )

    def test_non_identity_content_encoding_fails_explicitly(self) -> None:
        self.assert_error(
            HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_ENCODING,
            lambda: acquire_http(f"{self.base_url}/gzip", self.policy()),
        )

    def test_empty_response_fails_explicitly(self) -> None:
        self.assert_error(
            HttpAcquisitionErrorCode.EMPTY_BODY,
            lambda: acquire_http(f"{self.base_url}/empty", self.policy()),
        )

    def test_declared_oversized_response_fails_before_read(self) -> None:
        error = self.assert_error(
            HttpAcquisitionErrorCode.RESPONSE_TOO_LARGE,
            lambda: acquire_http(f"{self.base_url}/large", self.policy(max_bytes=16)),
        )
        self.assertIn("declared response size 64", error.detail)

    def test_streamed_oversized_response_fails_without_content_length(self) -> None:
        error = self.assert_error(
            HttpAcquisitionErrorCode.RESPONSE_TOO_LARGE,
            lambda: acquire_http(f"{self.base_url}/large-no-length", self.policy(max_bytes=16)),
        )
        self.assertIn("response body exceeds limit 16", error.detail)

    def test_missing_content_type_is_malformed_response(self) -> None:
        self.assert_error(
            HttpAcquisitionErrorCode.MALFORMED_RESPONSE,
            lambda: acquire_http(f"{self.base_url}/no-content-type", self.policy()),
        )

    def test_malformed_content_length_is_explicit(self) -> None:
        self.assert_error(
            HttpAcquisitionErrorCode.MALFORMED_RESPONSE,
            lambda: acquire_http(f"{self.base_url}/bad-length", self.policy()),
        )

    def test_timeout_is_distinct_from_generic_network_error(self) -> None:
        self.assert_error(
            HttpAcquisitionErrorCode.TIMEOUT,
            lambda: acquire_http(f"{self.base_url}/slow", self.policy(timeout_seconds=0.05)),
        )

    def test_freeze_writes_verified_content_addressed_snapshot(self) -> None:
        result = acquire_http(f"{self.base_url}/json", self.policy())
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "nested" / "snapshot.json"
            frozen = freeze_http_snapshot(result, destination)
            self.assertEqual(result.body, destination.read_bytes())
            self.assertEqual(str(destination), frozen.snapshot)
            self.assertTrue(verify_content_addressed_ref(frozen.content_ref))
            self.assertIn(result.sha256, frozen.content_ref)

    def test_existing_snapshot_is_not_overwritten_by_default(self) -> None:
        result = acquire_http(f"{self.base_url}/json", self.policy())
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "snapshot.json"
            destination.write_bytes(b"original")
            self.assert_error(
                HttpAcquisitionErrorCode.SNAPSHOT_EXISTS,
                lambda: freeze_http_snapshot(result, destination),
            )
            self.assertEqual(b"original", destination.read_bytes())

    def test_explicit_overwrite_replaces_snapshot_atomically(self) -> None:
        result = acquire_http(f"{self.base_url}/json", self.policy())
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "snapshot.json"
            destination.write_bytes(b"old")
            frozen = freeze_http_snapshot(result, destination, overwrite=True)
            self.assertEqual(result.body, destination.read_bytes())
            self.assertTrue(verify_content_addressed_ref(frozen.content_ref))

    def test_failed_acquisition_does_not_create_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "snapshot.txt"
            self.assert_error(
                HttpAcquisitionErrorCode.HTTP_STATUS,
                lambda: acquire_and_freeze_http(
                    f"{self.base_url}/error",
                    destination,
                    self.policy(),
                ),
            )
            self.assertFalse(destination.exists())

    def test_policy_rejects_invalid_limits_and_unapproved_schemes(self) -> None:
        with self.assertRaises(ValueError):
            DirectHttpPolicy(timeout_seconds=0)
        with self.assertRaises(ValueError):
            DirectHttpPolicy(max_bytes=True)
        with self.assertRaises(ValueError):
            DirectHttpPolicy(max_redirects=-1)
        with self.assertRaises(ValueError):
            DirectHttpPolicy(allowed_schemes=("file",))
        with self.assertRaises(ValueError):
            DirectHttpPolicy(allowed_content_types=("Text/Plain",))


if __name__ == "__main__":
    unittest.main()
