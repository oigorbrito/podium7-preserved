import sqlite3
from pathlib import Path
import tempfile
import unittest

from podium7.persistence import EvidenceStore, SCHEMA_VERSION


class PersistenceSchemaVersionTests(unittest.TestCase):
    def test_new_store_records_current_schema_version(self):
        with EvidenceStore() as store:
            self.assertEqual(store.schema_version, SCHEMA_VERSION)
            self.assertEqual(SCHEMA_VERSION, 1)

    def test_unversioned_existing_database_is_adopted_without_data_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "legacy.sqlite"
            connection = sqlite3.connect(database)
            connection.execute(
                "CREATE TABLE sources (id TEXT PRIMARY KEY, name TEXT NOT NULL, locator TEXT NOT NULL)"
            )
            connection.execute(
                "INSERT INTO sources(id, name, locator) VALUES (?, ?, ?)",
                ("legacy-source", "Legacy", "https://example.test/legacy"),
            )
            connection.commit()
            connection.close()

            with EvidenceStore(database) as store:
                self.assertEqual(store.schema_version, SCHEMA_VERSION)
                source = store.get_source("legacy-source")
                self.assertIsNotNone(source)
                self.assertEqual(source.name, "Legacy")

    def test_future_schema_version_is_rejected_without_downgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "future.sqlite"
            connection = sqlite3.connect(database)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")
            connection.commit()
            connection.close()

            with self.assertRaises(ValueError):
                EvidenceStore(database)

            connection = sqlite3.connect(database)
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            connection.close()
            self.assertEqual(version, SCHEMA_VERSION + 1)


if __name__ == "__main__":
    unittest.main()
