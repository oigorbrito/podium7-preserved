from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import venv


def _stage_source(root: Path, destination: Path) -> None:
    destination.mkdir(parents=True)
    for filename in ("pyproject.toml", "README.md"):
        shutil.copy2(root / filename, destination / filename)
    shutil.copytree(root / "podium7", destination / "podium7")


def _single_artifact(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {pattern} artifact, found {len(matches)}")
    return matches[0]


def _extract_sdist(sdist: Path, destination: Path) -> Path:
    destination.mkdir(parents=True)
    with tarfile.open(sdist, "r:gz") as archive:
        archive.extractall(destination, filter="data")
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError(f"expected one sdist root directory, found {len(roots)}")
    return roots[0]


def _venv_python(environment: Path) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def _build_requirements(root: Path) -> tuple[str, ...]:
    payload = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    build_system = payload.get("build-system")
    if not isinstance(build_system, dict):
        raise RuntimeError("pyproject.toml has no valid build-system table")
    backend = build_system.get("build-backend")
    if backend != "setuptools.build_meta":
        raise RuntimeError(f"unsupported build backend: {backend!r}")
    requirements = build_system.get("requires")
    if (
        not isinstance(requirements, list)
        or not requirements
        or not all(isinstance(requirement, str) and requirement.strip() for requirement in requirements)
    ):
        raise RuntimeError("pyproject.toml has invalid build-system requirements")
    return tuple(requirements)


def _has_setuptools_backend(python: Path) -> bool:
    probe = subprocess.run(
        [str(python), "-c", "from setuptools import build_meta; print(build_meta.__name__)"],
        capture_output=True,
        text=True,
    )
    return probe.returncode == 0


def _prepare_build_environment(root: Path, environment: Path) -> Path:
    del environment
    requirements = _build_requirements(root)
    if not all(requirement.startswith("setuptools") for requirement in requirements):
        raise RuntimeError(f"offline package check cannot satisfy build requirements: {requirements!r}")

    candidates = [Path(sys.executable)]
    if os.name != "nt":
        system_python = Path("/usr/bin/python3")
        if system_python.is_file() and system_python not in candidates:
            candidates.append(system_python)

    for python in candidates:
        if _has_setuptools_backend(python):
            return python
    raise RuntimeError("no preinstalled setuptools build backend is available for offline package check")


def _run_build_hook(python: Path, source: Path, dist: Path, hook: str) -> None:
    code = (
        "import os, sys; "
        "from setuptools import build_meta; "
        "os.chdir(sys.argv[1]); "
        "getattr(build_meta, sys.argv[2])(sys.argv[3])"
    )
    subprocess.run(
        [str(python), "-c", code, str(source), hook, str(dist)],
        check=True,
    )


def _validate_health(stdout: str) -> dict[str, object]:
    payload = json.loads(stdout.strip())
    if payload.get("status") != "PASS":
        raise RuntimeError(f"installed package health failed: {payload}")
    schema_version = payload.get("schema_version")
    expected = payload.get("expected_schema_version")
    if not isinstance(schema_version, int) or schema_version <= 0 or schema_version != expected:
        raise RuntimeError(f"installed package schema health is invalid: {payload}")
    return payload


def check_package_installation(root: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="podium7-package-check-") as tmp:
        workspace = Path(tmp)
        staged_source = workspace / "source"
        dist = workspace / "dist"
        extracted = workspace / "extracted"
        build_environment = workspace / "build-venv"
        install_environment = workspace / "install-venv"
        probe = workspace / "probe"
        dist.mkdir()
        probe.mkdir()

        _stage_source(root, staged_source)
        build_python = _prepare_build_environment(staged_source, build_environment)
        _run_build_hook(build_python, staged_source, dist, "build_sdist")
        sdist = _single_artifact(dist, "*.tar.gz")

        extracted_source = _extract_sdist(sdist, extracted)
        _run_build_hook(build_python, extracted_source, dist, "build_wheel")
        wheel = _single_artifact(dist, "*.whl")

        venv.EnvBuilder(with_pip=True, clear=True).create(install_environment)
        install_python = _venv_python(install_environment)
        subprocess.run(
            [
                str(install_python),
                "-m",
                "pip",
                "--disable-pip-version-check",
                "install",
                "--no-index",
                "--no-deps",
                str(wheel),
            ],
            check=True,
            cwd=probe,
        )
        health = subprocess.run(
            [str(install_python), "-m", "podium7", "health"],
            check=True,
            cwd=probe,
            capture_output=True,
            text=True,
        )
        payload = _validate_health(health.stdout)

        return {
            "status": "PASS",
            "sdist": sdist.name,
            "wheel": wheel.name,
            "health": payload,
        }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        result = check_package_installation(root)
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
