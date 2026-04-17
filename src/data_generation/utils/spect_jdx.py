"""Importing spectra from JDX files."""

from pathlib import Path
from typing import List, Tuple


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
