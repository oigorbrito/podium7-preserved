from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import socket
import threading
import unittest
from unittest.mock import patch

from podium7.bound_http_acquisition import (
    BoundNetworkTarget,
    _host_header,
    acquire_bound_http,
    resolve_bound_target,
)
from podium7.http_acquisition import DirectHttpPolicy, HttpAcquisitionError, HttpAcquisitionErrorCode


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):  # type: ignore[no-untyped-def]
        return

    def do_GET(self) -> None:
        if self.path == "/ok":
            body = b"bound-ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "0")
        self.end_headers()


class BoundHttpAcquisitionTests(unittest.TestCase):
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
        values = dict(
            timeout_seconds=1.0,
            max_bytes=1024,
            max_redirects=2,
            allowed_schemes=("http",),
            allow_private_network=True,
        )
        values.update(overrides)
        return DirectHttpPolicy(**values)

    def test_bound_transport_preserves_existing_response_contract(self) -> None:
        result = acquire_bound_http(f"{self.base_url}/ok", self.policy())
        self.assertEqual(200, result.status)
        self.assertEqual(b"bound-ok", result.body)
        self.assertEqual("text/plain", result.content_type)
        self.assertEqual(0, result.redirect_count)

    def test_redirect_is_resolved_and_bound_again(self) -> None:
        result = acquire_bound_http(f"{self.base_url}/redirect", self.policy())
        self.assertEqual(f"{self.base_url}/ok", result.final_url)
        self.assertEqual(1, result.redirect_count)

    def test_host_header_formats_hostname_and_scheme_specific_ports(self) -> None:
        self.assertEqual(
            "example.test",
            _host_header(BoundNetworkTarget("https", "example.test", 443, ("93.184.216.34",))),
        )
        self.assertEqual(
            "example.test:80",
            _host_header(BoundNetworkTarget("https", "example.test", 80, ("93.184.216.34",))),
        )
        self.assertEqual(
            "example.test:443",
            _host_header(BoundNetworkTarget("http", "example.test", 443, ("93.184.216.34",))),
        )

    def test_host_header_brackets_ipv6_literals(self) -> None:
        address = "2001:4860:4860::8888"
        self.assertEqual(
            f"[{address}]",
            _host_header(BoundNetworkTarget("https", address, 443, (address,))),
        )
        self.assertEqual(
            f"[{address}]:8443",
            _host_header(BoundNetworkTarget("https", address, 8443, (address,))),
        )

    def test_resolver_rejects_any_non_global_address_by_default(self) -> None:
        mixed = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
        ]
        with patch("podium7.bound_http_acquisition.socket.getaddrinfo", return_value=mixed):
            with self.assertRaises(HttpAcquisitionError) as caught:
                resolve_bound_target("https://example.test/path", DirectHttpPolicy())
        self.assertEqual(HttpAcquisitionErrorCode.UNSAFE_NETWORK_TARGET, caught.exception.code)

    def test_connection_receives_validated_ip_not_hostname(self) -> None:
        resolved = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))]
        with patch("podium7.bound_http_acquisition.socket.getaddrinfo", return_value=resolved), patch(
            "podium7.bound_http_acquisition.socket.create_connection",
            side_effect=OSError("stop after binding assertion"),
        ) as create_connection:
            with self.assertRaises(HttpAcquisitionError) as caught:
                acquire_bound_http(
                    "http://example.test/path",
                    DirectHttpPolicy(allowed_schemes=("http",)),
                )
        self.assertEqual(HttpAcquisitionErrorCode.NETWORK_ERROR, caught.exception.code)
        self.assertEqual(("93.184.216.34", 80), create_connection.call_args.args[0])

    def test_rebinding_to_private_address_fails_before_connect(self) -> None:
        first = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))]
        second = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]
        with patch(
            "podium7.bound_http_acquisition.socket.getaddrinfo",
            side_effect=[first, second],
        ), patch("podium7.bound_http_acquisition.socket.create_connection") as create_connection:
            resolve_bound_target("http://example.test/path", DirectHttpPolicy(allowed_schemes=("http",)))
            with self.assertRaises(HttpAcquisitionError) as caught:
                acquire_bound_http("http://example.test/path", DirectHttpPolicy(allowed_schemes=("http",)))
        self.assertEqual(HttpAcquisitionErrorCode.UNSAFE_NETWORK_TARGET, caught.exception.code)
        create_connection.assert_not_called()


if __name__ == "__main__":
    unittest.main()
