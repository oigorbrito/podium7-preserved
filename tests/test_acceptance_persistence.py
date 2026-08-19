from pathlib import Path
import unittest
from unittest.mock import patch

from podium7.acceptance import run_acceptance_slice
from podium7.persistence import EvidenceStore


class AcceptancePersistenceTests(unittest.TestCase):
    def test_acceptance_refuses_incomplete_persisted_canonical_reconstruction(self):
        with patch.object(EvidenceStore, "canonical_facts_for_entity", return_value=[]):
            with self.assertRaisesRegex(RuntimeError, "persisted canonical facts"):
                run_acceptance_slice(
                    Path("data/raw/vehicle-makes-models/artega.json"),
                    Path("data/raw/web/autoevolution-artega-gt-2010.txt"),
                )


if __name__ == "__main__":
    unittest.main()
