from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .evidence import content_addressed_ref, verify_content_addressed_ref


CURRENT_WEB_BENCHMARKS: tuple[tuple[str, str], ...] = (
    ("autoevolution", "benchmarks/web_extraction_source_family_corpus_v1.json"),
    ("fueleconomy_gov", "benchmarks/web_extraction_fueleconomy_source_family_v1.json"),
)
CURRENT_WEB_SNAPSHOT_PINS = "benchmarks/web_acquisition_snapshot_pins_v1.json"
_GIT_BLOB_SHA1 = re.compile(r"^[0-9a-f]{40}$")


class AcquisitionIssueCode(str, Enum):
    DUPLICATE_CASE_ID = "DUPLICATE_CASE_ID"
    DUPLICATE_SNAPSHOT = "DUPLICATE_SNAPSHOT"
    EMPTY_SNAPSHOT = "EMPTY_SNAPSHOT"
    HASH_MISMATCH = "HASH_MISMATCH"
    INVALID_SOURCE_URL = "INVALID_SOURCE_URL"
    MISSING_PIN = "MISSING_PIN"
    MISSING_SNAPSHOT = "MISSING_SNAPSHOT"
    ORPHAN_PIN = "ORPHAN_PIN"


@dataclass(frozen=True)
class FrozenAcquisitionEntry:
    source_family: str
    dataset_version: str
    case_id: str
    source_url: str
    snapshot: str
    expected_git_blob_sha1: str | None

    @property
    def key(self) -> tuple[str, str]:
        return (self.source_family, self.case_id)


@dataclass(frozen=True)
class FrozenAcquisitionManifest:
    entries: tuple[FrozenAcquisitionEntry, ...]
    orphan_pins: tuple[str, ...] = ()


@dataclass(frozen=True)
class FrozenAcquisitionEvidence:
    source_family: str
    case_id: str
    source_url: str
    snapshot: str
    git_blob_sha1: str
    content_ref: str
    size_bytes: int


@dataclass(frozen=True)
class AcquisitionIssue:
    code: AcquisitionIssueCode
    source_family: str | None
    case_id: str | None
    snapshot: str | None
    detail: str


@dataclass(frozen=True)
class FrozenAcquisitionReport:
    entries: tuple[FrozenAcquisitionEntry, ...]
    evidence: tuple[FrozenAcquisitionEvidence, ...]
    issues: tuple[AcquisitionIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues and len(self.evidence) == len(self.entries)

    def to_dict(self) -> dict[str, object]:
        source_families = sorted({entry.source_family for entry in self.entries})
        unique_urls = {entry.source_url for entry in self.entries}
        declared_snapshots = {entry.snapshot for entry in self.entries}
        return {
            "status": "PASS" if self.ok else "FAIL",
            "sourceFamilyCount": len(source_families),
            "sourceFamilies": source_families,
            "caseCount": len(self.entries),
            "uniqueSourceUrlCount": len(unique_urls),
            "declaredSnapshotCount": len(declared_snapshots),
            "verifiedSnapshotCount": len(self.evidence),
            "verifiedBytes": sum(item.size_bytes for item in self.evidence),
            "issueCount": len(self.issues),
            "issues": [
                {
                    "code": issue.code.value,
                    "sourceFamily": issue.source_family,
                    "caseId": issue.case_id,
                    "snapshot": issue.snapshot,
                    "detail": issue.detail,
                }
                for issue in self.issues
            ],
        }


def _load_json_object(path: Path) -> dict[str, object]:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant is not allowed: {value}")

    payload = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} root must be an object")
    return payload


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load_pins(root: Path) -> dict[str, str]:
    payload = _load_json_object(root / CURRENT_WEB_SNAPSHOT_PINS)
    pins = payload.get("pins")
    if not isinstance(pins, dict):
        raise ValueError("snapshot pins must be an object")

    normalized: dict[str, str] = {}
    for path_text, digest in pins.items():
        snapshot = _required_text(path_text, "snapshot pin path")
        expected = _required_text(digest, f"snapshot pin {snapshot}")
        if _GIT_BLOB_SHA1.fullmatch(expected) is None:
            raise ValueError(f"snapshot pin for {snapshot} must be a lowercase Git blob SHA-1")
        normalized[snapshot] = expected
    return normalized


def load_current_web_acquisition_manifest(root: str | Path = ".") -> FrozenAcquisitionManifest:
    repo_root = Path(root)
    pins = _load_pins(repo_root)
    entries: list[FrozenAcquisitionEntry] = []
    referenced_snapshots: set[str] = set()

    for source_family, benchmark_path in CURRENT_WEB_BENCHMARKS:
        payload = _load_json_object(repo_root / benchmark_path)
        dataset_version = _required_text(payload.get("datasetVersion"), f"{benchmark_path} datasetVersion")
        cases = payload.get("cases")
        if not isinstance(cases, list):
            raise ValueError(f"{benchmark_path} cases must be an array")

        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                raise ValueError(f"{benchmark_path} case {index} must be an object")
            case_id = _required_text(case.get("id"), f"{benchmark_path} case id")
            source_url = _required_text(case.get("sourceUrl"), f"{benchmark_path} sourceUrl")
            snapshot = _required_text(case.get("snapshot"), f"{benchmark_path} snapshot")
            referenced_snapshots.add(snapshot)
            entries.append(
                FrozenAcquisitionEntry(
                    source_family=source_family,
                    dataset_version=dataset_version,
                    case_id=case_id,
                    source_url=source_url,
                    snapshot=snapshot,
                    expected_git_blob_sha1=pins.get(snapshot),
                )
            )

    orphan_pins = tuple(sorted(set(pins) - referenced_snapshots))
    return FrozenAcquisitionManifest(tuple(entries), orphan_pins)


def _valid_source_url(value: str) -> bool:
    parsed = urlsplit(value)
    return (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
        and parsed.fragment == ""
    )


def evaluate_frozen_web_acquisition(
    manifest: FrozenAcquisitionManifest,
    root: str | Path = ".",
) -> FrozenAcquisitionReport:
    repo_root = Path(root)
    issues: list[AcquisitionIssue] = []
    evidence: list[FrozenAcquisitionEvidence] = []
    seen_keys: set[tuple[str, str]] = set()
    seen_snapshots: set[str] = set()

    for orphan in manifest.orphan_pins:
        issues.append(
            AcquisitionIssue(
                AcquisitionIssueCode.ORPHAN_PIN,
                None,
                None,
                orphan,
                "snapshot pin is not referenced by either current web benchmark",
            )
        )

    for entry in manifest.entries:
        blocked = False
        if entry.key in seen_keys:
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.DUPLICATE_CASE_ID,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    "source-family case identity is duplicated",
                )
            )
            blocked = True
        else:
            seen_keys.add(entry.key)

        if entry.snapshot in seen_snapshots:
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.DUPLICATE_SNAPSHOT,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    "one frozen snapshot is owned by more than one benchmark case",
                )
            )
            blocked = True
        else:
            seen_snapshots.add(entry.snapshot)

        if not _valid_source_url(entry.source_url):
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.INVALID_SOURCE_URL,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    "source URL must be an exact credential-free HTTPS locator without a fragment",
                )
            )
            blocked = True

        if entry.expected_git_blob_sha1 is None:
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.MISSING_PIN,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    "snapshot has no pinned repository blob identity",
                )
            )
            blocked = True

        snapshot_path = repo_root / entry.snapshot
        if not snapshot_path.is_file():
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.MISSING_SNAPSHOT,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    "frozen snapshot file does not exist",
                )
            )
            continue

        data = snapshot_path.read_bytes()
        # Normalize CRLF to LF to match Git blob hashes generated on LF systems
        data = data.replace(b"\r\n", b"\n")
        if not data:
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.EMPTY_SNAPSHOT,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    "frozen snapshot is empty",
                )
            )
            continue

        actual_blob_sha1 = git_blob_sha1(data)
        if entry.expected_git_blob_sha1 is not None and actual_blob_sha1 != entry.expected_git_blob_sha1:
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.HASH_MISMATCH,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    f"expected Git blob {entry.expected_git_blob_sha1}, observed {actual_blob_sha1}",
                )
            )
            blocked = True

        actual_path = repo_root / entry.snapshot
        content_ref = content_addressed_ref(actual_path)
        if not verify_content_addressed_ref(content_ref):
            issues.append(
                AcquisitionIssue(
                    AcquisitionIssueCode.HASH_MISMATCH,
                    entry.source_family,
                    entry.case_id,
                    entry.snapshot,
                    "generated SHA-256 content reference did not verify",
                )
            )
            blocked = True

        if not blocked:
            evidence.append(
                FrozenAcquisitionEvidence(
                    source_family=entry.source_family,
                    case_id=entry.case_id,
                    source_url=entry.source_url,
                    snapshot=entry.snapshot,
                    git_blob_sha1=actual_blob_sha1,
                    content_ref=content_ref,
                    size_bytes=len(data),
                )
            )

    return FrozenAcquisitionReport(tuple(manifest.entries), tuple(evidence), tuple(issues))


def evaluate_current_web_acquisition(root: str | Path = ".") -> FrozenAcquisitionReport:
    return evaluate_frozen_web_acquisition(load_current_web_acquisition_manifest(root), root)
