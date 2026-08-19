import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from podium7.__main__ import _health_payload, main
from podium7.persistence import SCHEMA_VERSION


class RuntimeHealthTests(unittest.TestCase):
    def test_health_payload_reports_current_schema(self):
        payload = _health_payload()
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["expected_schema_version"], SCHEMA_VERSION)

    def test_health_command_prints_json_and_returns_zero(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = main(["health"])
        self.assertEqual(result, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)

    def test_health_command_returns_nonzero_on_failure(self):
        output = io.StringIO()
        with patch("podium7.__main__._health_payload", side_effect=RuntimeError("boom")):
            with redirect_stdout(output):
                result = main(["health"])
        self.assertEqual(result, 1)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "FAIL")
        self.assertIn("boom", payload["error"])


if __name__ == "__main__":
    unittest.main()
