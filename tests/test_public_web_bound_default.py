from __future__ import annotations

import unittest

from podium7.bound_http_acquisition import acquire_bound_http
from podium7.public_web_acquisition_benchmark import evaluate_public_web_acquisition


class PublicWebBoundDefaultTests(unittest.TestCase):
    def test_default_real_network_callback_uses_bound_transport(self) -> None:
        defaults = evaluate_public_web_acquisition.__kwdefaults__
        self.assertIsNotNone(defaults)
        self.assertIs(acquire_bound_http, defaults["acquire"])


if __name__ == "__main__":
    unittest.main()
