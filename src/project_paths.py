"""Shared path resolution helpers for the repository."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict


REPO_ROOT = Path(__file__).resolve().parents[1]
PATHS_FILE = REPO_ROOT / "src" / "paths.env"


@lru_cache(maxsize=1)
def _load_relative_paths() -> Dict[str, str]:
    paths: Dict[str, str] = {}
    with PATHS_FILE.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            paths[key.strip()] = value.strip().strip('"').strip("'")
    return paths


def shared_path(key: str, *parts: str) -> Path:
    """Resolve a configured relative path key against the repository root."""
    relative = _load_relative_paths()[key]
    path = REPO_ROOT / relative
    for part in parts:
        path = path / part
    return path


def repo_path(*parts: str) -> Path:
    """Resolve an arbitrary repository-relative path."""
    path = REPO_ROOT
    for part in parts:
        path = path / part
    return path


__all__ = ["REPO_ROOT", "PATHS_FILE", "shared_path", "repo_path"]
