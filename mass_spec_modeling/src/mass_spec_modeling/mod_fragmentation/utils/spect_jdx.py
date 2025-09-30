"""importing Spectra from JDX Files"""

from pathlib import Path
from typing import List, Tuple

def get_spectra_from_local_jdx(
    name: str,
    folder: Path = Path("/home/mescalin/reiserp/Nextcloud/" \
        "studium/computationalScience/thesis/mol/" \
        "mass_spec_modeling/exec_scripts/ms_data/nist_spectra/")
    ) -> List[Tuple[float, float]]:
    """Get spectra from local JDX file."""

    jdx_file = folder / f"{name.lower()}-Mass.jdx"

    if not jdx_file.exists():
        raise FileNotFoundError(f"JDX file for {name} not found at {jdx_file}")

    with open(jdx_file, encoding="utf-8") as f:
        spectra = []
        parsing_peaks = False
        for line in f:

            # only parse after the ##PEAK section
            if line.startswith("##PEAK"):
                parsing_peaks = True
            if line.startswith("##END"):
                break

            if parsing_peaks:
                try:
                    for xy in line.split():
                        mz, intensity = map(int, xy.split(","))
                        spectra.append((mz, intensity))
                except ValueError:
                    continue

    return spectra
