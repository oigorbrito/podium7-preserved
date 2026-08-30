from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import importlib.util
from io import StringIO
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from podium7.http_acquisition import DirectHttpAcquisition, FrozenHttpSnapshot


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "acquire_http_snapshot.py"
SPEC = importlib.util.spec_from_file_location("podium7_acquire_http_snapshot_script", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load acquire_http_snapshot script")
SCRIPT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCRIPT)


class AcquireHttpSnapshotScriptTests(unittest.TestCase):
    def test_cli_uses_bound_transport_then_freezes_exact_acquisition(self):
        url = "https://example.com/source"
        destination = "snapshot.html"
        body = b"source bytes"
        acquisition = DirectHttpAcquisition(
            requested_url=url,
            final_url=url,
            redirect_count=0,
            status=200,
            content_type="text/html",
            charset="utf-8",
            body=body,
            sha256=hashlib.sha256(body).hexdigest(),
        )
        frozen = FrozenHttpSnapshot(
            acquisition=acquisition,
            snapshot=destination,
            content_ref=f"sha256:{acquisition.sha256}:{destination}",
        )

        output = StringIO()
        with (
            patch.object(SCRIPT, "acquire_bound_http", return_value=acquisition) as acquire,
            patch.object(SCRIPT, "freeze_http_snapshot", return_value=frozen) as freeze,
            redirect_stdout(output),
        ):
            exit_code = SCRIPT.main(
                [
                    url,
                    destination,
                    "--timeout-seconds",
                    "7",
                    "--max-bytes",
                    "1234",
                    "--max-redirects",
                    "2",
                    "--overwrite",
                ]
            )

        self.assertEqual(0, exit_code)
        acquire.assert_called_once()
        called_url, policy = acquire.call_args.args
        self.assertEqual(url, called_url)
        self.assertEqual(7.0, policy.timeout_seconds)
        self.assertEqual(1234, policy.max_bytes)
        self.assertEqual(2, policy.max_redirects)
        freeze.assert_called_once_with(acquisition, destination, overwrite=True)
        payload = json.loads(output.getvalue())
        self.assertEqual("PASS", payload["status"])
        self.assertEqual(acquisition.sha256, payload["sha256"])


if __name__ == "__main__":
    unittest.main()
