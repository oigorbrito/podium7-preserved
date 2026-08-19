from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


def _iter_test_ids(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_test_ids(item)
        else:
            yield item.id()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tests_dir = root / "tests"

    loader = unittest.TestLoader()
    discovered = loader.discover(str(tests_dir), pattern="test_*.py")
    test_ids = sorted(set(_iter_test_ids(discovered)))

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
