import json
from pathlib import Path
import unittest

from podium7.official_discovery import (
    discover_fueleconomy_models,
    discover_fueleconomy_vehicle_options,
    discover_nhtsa_models,
)


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmarks" / "official_source_discovery_v1.json"


class OfficialDiscoveryBenchmarkTests(unittest.TestCase):
    def test_all_benchmark_cases_match_declared_candidate_contract(self):
        payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        self.assertEqual(payload["schemaVersion"], 1)
        for case in payload["cases"]:
            request = case["request"]
            if case["source"] == "nhtsa_vpic":
                candidates = discover_nhtsa_models(
                    case["payload"], make=request["make"], model_year=request["modelYear"]
                )
            elif "model" in request:
                candidates = discover_fueleconomy_vehicle_options(
                    case["payload"],
                    make=request["make"],
                    model=request["model"],
                    model_year=request["modelYear"],
                )
            else:
                candidates = discover_fueleconomy_models(
                    case["payload"], make=request["make"], model_year=request["modelYear"]
                )
            self.assertEqual(len(candidates), case["expectedCandidateCount"], case["id"])
            self.assertTrue(all(candidate.identity_proof is case["expectedIdentityProof"] for candidate in candidates))
            if "expectedVehicleId" in case:
                self.assertEqual(candidates[0].source_vehicle_id, case["expectedVehicleId"])


if __name__ == "__main__":
    unittest.main()
