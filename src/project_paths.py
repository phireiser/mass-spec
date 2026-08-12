"""Shared path resolution helpers for the repository.

Every filesystem path used by src/ and run/ is declared once in src/paths.env;
this module is the Python reader for it. See that file for the naming rules.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Dict


REPO_ROOT = Path(__file__).resolve().parents[1]

# Bootstrap: "src" is spelled out here rather than taken from SRC_DIR_REL because
# this is the file that locates the file which defines SRC_DIR_REL. The guardrail
# test in src/tests/unit_test_project_paths.py allowlists exactly this one line.
PATHS_FILE = REPO_ROOT / "src" / "paths.env"

_REFERENCE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@lru_cache(maxsize=1)
def _load_relative_paths() -> Dict[str, str]:
    """Parse paths.env, expanding ${KEY} references against earlier keys.

    Forward-only, matching what bash `source` does: a key must be defined above
    its first use. An unknown or forward reference is an error rather than a
    silently-literal "${FOO}" directory name.
    """
    paths: Dict[str, str] = {}
    with PATHS_FILE.open("r", encoding="utf-8") as handle:
        for lineno, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            def _expand(match: re.Match[str], _lineno: int = lineno) -> str:
                name = match.group(1)
                if name not in paths:
                    raise KeyError(
                        f"{PATHS_FILE}:{_lineno}: ${{{name}}} is not defined above "
                        f"this line. Keys may only reference earlier keys."
                    )
                return paths[name]

            paths[key] = _REFERENCE.sub(_expand, value)
    return paths


def _lookup(key: str) -> str:
    paths = _load_relative_paths()
    try:
        return paths[key]
    except KeyError:
        raise KeyError(
            f"{key!r} is not defined in {PATHS_FILE}. Available keys: "
            f"{', '.join(sorted(paths))}"
        ) from None


def shared_path(key: str, *parts: str) -> Path:
    """Resolve a configured path key against the repository root."""
    path = REPO_ROOT / _lookup(key)
    for part in parts:
        path = path / part
    return path


def shared_name(key: str) -> str:
    """Leaf name of a configured path, for joining onto a caller-supplied root.

    Use where a directory is nested under a root the caller chooses at runtime --
    e.g. `--output-dir` overrides for the fwd/bwd dump directories -- so the leaf
    name is still declared only in paths.env.
    """
    return PurePosixPath(_lookup(key)).name


def repo_path(*parts: str) -> Path:
    """Resolve an arbitrary repository-relative path."""
    path = REPO_ROOT
    for part in parts:
        path = path / part
    return path


__all__ = [
    "REPO_ROOT",
    "PATHS_FILE",
    "shared_path",
    "shared_name",
    "repo_path",
]
