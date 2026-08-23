from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import sys
from urllib.parse import unquote


MAX_AGENTS_LINES = 60
MAX_CURRENT_WORK_LINES = 100
MAX_STATE_AGE_DAYS = 60
REQUIRED_PATHS = (
    "AGENTS.md",
    "docs/INDEX.md",
    "docs/CURRENT-STATE.md",
    "docs/CURRENT-WORK.md",
    "docs/DEVELOPMENT-WORKFLOW.md",
    "docs/INVARIANTS.md",
    "docs/TECH-DEBT.md",
    "docs/exec-plans/README.md",
    "docs/exec-plans/active/README.md",
    "docs/exec-plans/completed/README.md",
    "docs/exec-plans/completed/2026-08-22-agent-harness-v1.md",
    "docs/references/OPENAI-CODEX-HARNESS.md",
    "docs/generated/README.md",
    "scripts/project_facts.py",
)
AGENT_LINK_TARGETS = (
    "docs/INDEX.md",
    "docs/CURRENT-STATE.md",
    "docs/CURRENT-WORK.md",
    "docs/DEVELOPMENT-WORKFLOW.md",
    "docs/INVARIANTS.md",
    "docs/TECH-DEBT.md",
)
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FRESHNESS_RE = re.compile(r"^Last verified:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
VOLATILE_PATTERNS = (
    re.compile(r"\b\d+\s*/\s*\d+\s+(?:tests?|testes)\b", re.IGNORECASE),
    re.compile(r"\bPython\s+\d+\.\d+(?:\.\d+)?\b"),
    re.compile(r"\b[0-9a-f]{40}\b"),
    re.compile(r"\btests?_discovered\s*[:=]\s*\d+\b", re.IGNORECASE),
)


class HarnessError(ValueError):
    pass


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_paths(root: Path) -> None:
    missing = [path for path in REQUIRED_PATHS if not (root / path).is_file()]
    if missing:
        raise HarnessError("missing required harness paths: " + ", ".join(missing))


def _check_agents(root: Path) -> None:
    path = root / "AGENTS.md"
    text = _text(path)
    lines = text.splitlines()
    if len(lines) > MAX_AGENTS_LINES:
        raise HarnessError(
            f"AGENTS.md must remain a short map (<= {MAX_AGENTS_LINES} lines); found {len(lines)}"
        )
    for target in AGENT_LINK_TARGETS:
        if f"({target})" not in text:
            raise HarnessError(f"AGENTS.md must link to canonical source: {target}")
    forbidden_headings = ("## Testing", "## Git", "## Default autonomy", "## Product constraints")
    for heading in forbidden_headings:
        if heading in text:
            raise HarnessError(
                f"AGENTS.md contains policy section {heading!r}; policy belongs in canonical docs"
            )


def _resolve_link(source: Path, target: str, root: Path) -> Path | None:
    target = target.strip().split()[0]
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target:
        return None
    candidate = (source.parent / target).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise HarnessError(f"link escapes repository: {source.relative_to(root)} -> {target}") from exc
    return candidate


def _check_links(root: Path) -> None:
    markdown_paths = [root / "AGENTS.md", root / "README.md", *sorted((root / "docs").rglob("*.md"))]
    broken: list[str] = []
    for source in markdown_paths:
        for target in LINK_RE.findall(_text(source)):
            resolved = _resolve_link(source, target, root)
            if resolved is not None and not resolved.exists():
                broken.append(f"{source.relative_to(root)} -> {target}")
    if broken:
        raise HarnessError("broken relative Markdown links: " + " | ".join(broken))


def _check_index(root: Path) -> None:
    index = _text(root / "docs" / "INDEX.md")
    missing: list[str] = []
    for path in sorted((root / "docs").glob("*.md")):
        if path.name == "INDEX.md":
            continue
        if f"({path.name})" not in index:
            missing.append(path.name)
    if missing:
        raise HarnessError("top-level docs missing from docs/INDEX.md: " + ", ".join(missing))


def _check_freshness(root: Path) -> None:
    for relative in ("docs/CURRENT-STATE.md", "docs/references/OPENAI-CODEX-HARNESS.md"):
        text = _text(root / relative)
        match = FRESHNESS_RE.search(text)
        if match is None:
            raise HarnessError(f"{relative} must contain 'Last verified: YYYY-MM-DD'")
        verified = date.fromisoformat(match.group(1))
        age = (date.today() - verified).days
        if age < 0:
            raise HarnessError(f"{relative} freshness date is in the future")
        if age > MAX_STATE_AGE_DAYS:
            raise HarnessError(
                f"{relative} is stale ({age} days); verify and refresh within {MAX_STATE_AGE_DAYS} days"
            )


def _check_current_state(root: Path) -> None:
    for relative in ("docs/CURRENT-STATE.md", "docs/CURRENT-WORK.md"):
        text = _text(root / relative)
        for pattern in VOLATILE_PATTERNS:
            match = pattern.search(text)
            if match:
                raise HarnessError(
                    f"{relative} manually transcribes volatile fact {match.group(0)!r}; use scripts/project_facts.py"
                )
    work_lines = _text(root / "docs" / "CURRENT-WORK.md").splitlines()
    if len(work_lines) > MAX_CURRENT_WORK_LINES:
        raise HarnessError(
            f"docs/CURRENT-WORK.md must stay current/short (<= {MAX_CURRENT_WORK_LINES} lines)"
        )
    if not re.search(r"^Status:\s*(active|none|blocked)\s*$", "\n".join(work_lines), re.MULTILINE):
        raise HarnessError("docs/CURRENT-WORK.md must declare Status: active|none|blocked")


def check_harness(root: Path) -> None:
    _require_paths(root)
    _check_agents(root)
    _check_links(root)
    _check_index(root)
    _check_freshness(root)
    _check_current_state(root)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        check_harness(root)
    except (OSError, HarnessError, ValueError) as exc:
        print(f"HARNESS FAIL: {exc}")
        return 2
    print("HARNESS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
