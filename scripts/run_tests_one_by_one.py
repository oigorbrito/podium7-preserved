from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import sys


def _is_test_case_class(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Attribute) and base.attr == "TestCase":
            return True
        if isinstance(base, ast.Name) and base.id == "TestCase":
            return True
    return False


def _discover_test_ids(tests_dir: Path) -> list[str]:
    test_ids: list[str] = []
    for path in sorted(tests_dir.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not _is_test_case_class(node):
                continue
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name.startswith("test_"):
                    test_ids.append(f"{path.stem}.{node.name}.{member.name}")
    return sorted(test_ids)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tests_dir = root / "tests"
    test_ids = _discover_test_ids(tests_dir)

    if not test_ids:
        print("FAIL — no tests discovered")
        return 2

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    pythonpath_parts = [str(root), str(tests_dir)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    total = len(test_ids)
    for index, test_id in enumerate(test_ids, start=1):
        print(f"[{index}/{total}] RUN {test_id}", flush=True)
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", test_id],
            cwd=root,
            env=env,
            check=False,
        )
        if completed.returncode != 0:
            print(f"[{index}/{total}] FAIL {test_id}", flush=True)
            return completed.returncode
        print(f"[{index}/{total}] PASS {test_id}", flush=True)

    print(f"PASS — {total}/{total} tests executed one by one", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
