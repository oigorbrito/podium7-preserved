import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from scripts.check_harness import (
    HarnessError,
    MAX_AGENTS_LINES,
    MAX_CURRENT_WORK_LINES,
    _check_agents,
    _check_current_state,
    _check_freshness,
    _check_index,
    _check_links,
    _require_paths,
    check_harness,
)
from scripts.project_facts import REPORT_SCHEMA, build_project_facts


ROOT = Path(__file__).resolve().parents[1]


class AgentHarnessTests(unittest.TestCase):
    def test_01_repository_harness_passes(self) -> None:
        check_harness(ROOT)

    def test_02_agents_is_bounded_map(self) -> None:
        lines = (ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), MAX_AGENTS_LINES)

    def test_03_docs_index_exists(self) -> None:
        self.assertTrue((ROOT / "docs" / "INDEX.md").is_file())

    def test_04_workflow_is_canonical_link_from_agents(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("(docs/DEVELOPMENT-WORKFLOW.md)", text)

    def test_05_invariants_are_canonical_link_from_agents(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("(docs/INVARIANTS.md)", text)

    def test_06_project_facts_schema(self) -> None:
        facts = build_project_facts(ROOT)
        self.assertEqual(facts["schema"], REPORT_SCHEMA)

    def test_07_project_facts_derive_test_count(self) -> None:
        facts = build_project_facts(ROOT)
        self.assertGreater(facts["tests_discovered"], 0)

    def test_08_project_facts_derive_runtime_health(self) -> None:
        facts = build_project_facts(ROOT)
        self.assertTrue(facts["runtime"]["ready"])

    def test_09_project_facts_derive_release_blocker(self) -> None:
        facts = build_project_facts(ROOT)
        self.assertFalse(facts["release"]["ready"])
        self.assertIn("license", facts["release"]["message"].lower())

    def test_10_project_facts_derive_benchmark_counts(self) -> None:
        facts = build_project_facts(ROOT)["catalog_identity_benchmarks"]
        self.assertGreaterEqual(facts["dataset_count"], 2)
        self.assertEqual(sum(facts["labels"].values()), facts["case_count"])

    def test_11_project_facts_derive_scientific_reference_count(self) -> None:
        facts = build_project_facts(ROOT)
        self.assertGreaterEqual(facts["scientific_reference_count"], 1)

    def test_12_missing_required_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(HarnessError, "missing required"):
                _require_paths(Path(directory))

    def test_13_bloated_agents_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            links = "\n".join(
                f"[{target}]({target})"
                for target in (
                    "docs/INDEX.md",
                    "docs/CURRENT-STATE.md",
                    "docs/CURRENT-WORK.md",
                    "docs/DEVELOPMENT-WORKFLOW.md",
                    "docs/INVARIANTS.md",
                    "docs/TECH-DEBT.md",
                )
            )
            (root / "AGENTS.md").write_text(
                links + "\n" + "\n".join("x" for _ in range(MAX_AGENTS_LINES + 1)),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(HarnessError, "short map"):
                _check_agents(root)

    def test_14_agents_policy_heading_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = "\n".join(
                f"[{target}]({target})"
                for target in (
                    "docs/INDEX.md",
                    "docs/CURRENT-STATE.md",
                    "docs/CURRENT-WORK.md",
                    "docs/DEVELOPMENT-WORKFLOW.md",
                    "docs/INVARIANTS.md",
                    "docs/TECH-DEBT.md",
                )
            ) + "\n## Testing\n"
            (root / "AGENTS.md").write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "policy section"):
                _check_agents(root)

    def test_15_agents_missing_canonical_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# map\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "canonical source"):
                _check_agents(root)

    def test_16_broken_relative_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "AGENTS.md").write_text("[bad](docs/missing.md)\n", encoding="utf-8")
            (root / "README.md").write_text("# readme\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "broken relative"):
                _check_links(root)

    def test_17_external_link_is_not_local_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "AGENTS.md").write_text("[OpenAI](https://openai.com/)\n", encoding="utf-8")
            (root / "README.md").write_text("# readme\n", encoding="utf-8")
            _check_links(root)

    def test_18_link_escaping_repository_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "AGENTS.md").write_text("[bad](../outside.md)\n", encoding="utf-8")
            (root / "README.md").write_text("# readme\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "escapes repository"):
                _check_links(root)

    def test_19_unindexed_top_level_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "INDEX.md").write_text("# index\n", encoding="utf-8")
            (docs / "ORPHAN.md").write_text("# orphan\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "missing from docs/INDEX"):
                _check_index(root)

    def test_20_stale_current_state_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            refs = root / "docs" / "references"
            refs.mkdir(parents=True)
            stale = (date.today() - timedelta(days=61)).isoformat()
            (root / "docs" / "CURRENT-STATE.md").write_text(
                f"Last verified: {stale}\n", encoding="utf-8"
            )
            (refs / "OPENAI-CODEX-HARNESS.md").write_text(
                f"Last verified: {date.today().isoformat()}\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(HarnessError, "stale"):
                _check_freshness(root)

    def test_21_future_freshness_date_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            refs = root / "docs" / "references"
            refs.mkdir(parents=True)
            future = (date.today() + timedelta(days=1)).isoformat()
            (root / "docs" / "CURRENT-STATE.md").write_text(
                f"Last verified: {future}\n", encoding="utf-8"
            )
            (refs / "OPENAI-CODEX-HARNESS.md").write_text(
                f"Last verified: {date.today().isoformat()}\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(HarnessError, "future"):
                _check_freshness(root)

    def test_22_manual_test_counter_in_state_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "CURRENT-STATE.md").write_text("237/237 tests\n", encoding="utf-8")
            (docs / "CURRENT-WORK.md").write_text("Status: active\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "volatile fact"):
                _check_current_state(root)

    def test_23_manual_sha_in_work_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "CURRENT-STATE.md").write_text("stable\n", encoding="utf-8")
            (docs / "CURRENT-WORK.md").write_text(
                "Status: active\n" + "a" * 40 + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(HarnessError, "volatile fact"):
                _check_current_state(root)

    def test_24_current_work_must_stay_short(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "CURRENT-STATE.md").write_text("stable\n", encoding="utf-8")
            (docs / "CURRENT-WORK.md").write_text(
                "Status: active\n" + "\n".join("x" for _ in range(MAX_CURRENT_WORK_LINES + 1)),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(HarnessError, "current/short"):
                _check_current_state(root)

    def test_25_current_work_requires_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "CURRENT-STATE.md").write_text("stable\n", encoding="utf-8")
            (docs / "CURRENT-WORK.md").write_text("# work\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "Status"):
                _check_current_state(root)


if __name__ == "__main__":
    unittest.main()
