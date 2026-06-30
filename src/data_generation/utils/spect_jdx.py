"""Importing spectra from JDX files."""

from pathlib import Path
from typing import Dict, List, Tuple


def parse_jdx_header(
        file: Path
    ) -> Dict[str, str]:
    """Parse the ``##KEY=VALUE`` header records of a JDX Mass file.

    Returns a dict keyed by the bare record name (e.g. ``"MOLFORM"``, ``"MW"``,
    ``"TITLE"``) mapped to its raw string value. Reading stops at the peak table.
    Multi-line continuation records are not joined (only the first line is kept),
    which is sufficient for the scalar fields Phase 0 needs.
    """
    if not file.exists():
        raise FileNotFoundError(f"JDX file not found: {file}")
    header: Dict[str, str] = {}
    with open(file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("##PEAK") or line.startswith("##END"):
                break
            if line.startswith("##"):
                key, sep, value = line[2:].partition("=")
                if sep:
                    header[key.strip().lstrip("$").upper()] = value.strip()
    return header


def parse_jdx(
        file: Path
    ) -> List[Tuple[float, float]]:
    """Parse a JDX Mass file defensively and return (mz, intensity) tuples."""
    if not file.exists():
        raise FileNotFoundError(f"JDX file not found: {file}")
    spectra: List[Tuple[float, float]] = []
    with open(file, encoding="utf-8") as f:
        parsing_peaks = False
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("##PEAK"):
                parsing_peaks = True
                continue
            if line.startswith("##END"):
                break
            if parsing_peaks:
                for token in line.split():
                    try:
                        mz_str, inten_str = token.split(",")
                        mz = float(mz_str); inten = float(inten_str)
                        spectra.append((mz, inten))
                    except Exception:
                        # skip malformed tokens
                        continue
    return spectra


def get_spectra_from_local_jdx(
    name: str,
    folder: Path,
    ) -> List[Tuple[float, float]]:
    """Resolve file by name within the project spectra folder and parse via parse_jdx."""
    jdx_file = folder / f"{name.lower()}-Mass.jdx"
    return parse_jdx(jdx_file)


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "get_spectra_from_local_jdx",
    "parse_jdx",
    "parse_jdx_header",
]
