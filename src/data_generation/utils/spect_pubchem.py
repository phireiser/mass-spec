"""
PubChem utilities reworked to use a client and parser for SOLID compliance.
"""
from typing import List, Tuple, Dict, Any
from collections import defaultdict
from math import isfinite

from .pubchem_client import PubChemClient
from .pubchem_parser import get_spectra_from_information_section, find_gc_ms_sections


def pubchem_smiles_lookup(smiles: str) -> int:
    client = PubChemClient()
    return client.smiles_to_cid(smiles)


def get_information_section_from_pubchem(cid: int) -> List[Dict[str, Any]] | None:
    client = PubChemClient()
    data = client.fetch_compound_view(cid)

    sections = find_gc_ms_sections(data)
    if not sections:
        return None

    # First GC-MS section containing Information
    for s in sections:
        for info in s.get("Information", []) or []:
            return info
        if section.get("TOCHeading") == "GC-MS":
            return section.get("Information")
        # Search deeper if nested
        result = find_gc_ms(section.get("Section", []))
        if result is not None:
            return result
        return None

    gc_ms_info = find_gc_ms(data.get("Record", {}).get("Section", []))

    if gc_ms_info:
        return gc_ms_info

    raise RuntimeError(f"No GC-MS data found for compound {cid}")

def clean_spectra(
    spectra: List[Dict[int, List[Tuple[float, float]]]]
    ) -> List[Tuple[int, float]]:
    """
    Combine and clean PubChem peak lists.
    Flattens all reference spectra into one set of peaks.

    - Bins m/z to nearest integer (common for EI spectra tables).
    - Sums intensities for identical bins across references.
    - Normalizes intensities so the base peak is 100.0.
    - Returns peaks sorted by m/z.
    """
    bins: Dict[int, float] = defaultdict(float)

    for ref_block in spectra:
        for _ref_id, peaks in ref_block.items():
            for mz, inten in peaks:
                # basic sanity checks
                if not (isinstance(mz, (int, float)) and isinstance(inten, (int, float))):
                    continue
                if not (isfinite(mz) and isfinite(inten)):
                    continue
                if inten <= 0:
                    continue
                mz_bin = int(round(mz))
                if mz_bin <= 0:
                    continue
                bins[mz_bin] += float(inten)

    if not bins:
        return []

    base = max(bins.values())
    if base <= 0:
        return []

    cleaned = [(mzi, (inten / base) * 100.0) for mzi, inten in bins.items()]
    cleaned.sort(key=lambda x: x[0])  # sort by m/z

    return cleaned



def get_spectra_from_pubchem(
    smiles: str
    ) -> List[Dict[int, List[Tuple[float, float]]]]:
    """
    Chaining of the PubChem functions to get spectra.
    """
    cid = pubchem_smiles_lookup(smiles)
    info = get_information_section_from_pubchem(cid)
    spectra = get_spectra_from_information_section(info)
    clean = clean_spectra(spectra)
    return clean
