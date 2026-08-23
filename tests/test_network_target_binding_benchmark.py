from __future__ import annotations

import json
from pathlib import Path
import unittest


class NetworkTargetBindingBenchmarkTests(unittest.TestCase):
    def test_contract_inventory_is_stable(self) -> None:
        payload = json.loads(Path("benchmarks/network_target_binding_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(1, payload["schemaVersion"])
        self.assertEqual("LOCALLY_VERIFIED_SECURITY_CONTRACT", payload["evidenceClass"])
        self.assertEqual(
            [
                "validated-ip-is-socket-target",
                "mixed-global-private-resolution",
                "rebind-global-to-private-before-connect",
                "redirect-reresolves-and-rebinds",
            ],
            [case["id"] for case in payload["cases"]],
        )


if __name__ == "__main__":
    unittest.main()
