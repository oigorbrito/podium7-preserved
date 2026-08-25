from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from podium7.__main__ import _require_review_database
from podium7.catalog import CatalogStore
from podium7.catalog_review import CatalogReviewQueue


class CatalogReviewOperatorCanonicalPathV1Tests(unittest.TestCase):
    def test_preflight_returns_the_same_canonical_path_it_validates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "catalog.sqlite"
            with CatalogStore(target) as store:
                CatalogReviewQueue(store)

            alias = Path(directory) / "catalog-link.sqlite"
            try:
                alias.symlink_to(target)
            except OSError as exc:
                if getattr(exc, "winerror", None) == 1314:
                    self.skipTest("symlink privilege is unavailable on this Windows runner")
                raise

            validated = _require_review_database(str(alias))

            self.assertEqual(validated, target.resolve())
            self.assertFalse(validated.is_symlink())


if __name__ == "__main__":
    unittest.main()
