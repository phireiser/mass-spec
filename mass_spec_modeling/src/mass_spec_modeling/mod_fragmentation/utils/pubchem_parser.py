"""
Stateless parsers for PubChem information sections to spectra.
"""
from typing import List, Tuple, Dict, Any

FIELDS_TOP5 = {"Top 5 Peaks"}
FIELDS_TOP3 = {"m/z Top Peak", "m/z 2nd Highest", "m/z 3rd Highest"}


def get_spectra_from_information_section(information: List[Dict[str, Any]]) -> List[Dict[int, List[Tuple[float, float]]]]:
    spectra: List[Dict[int, List[Tuple[float, float]]]] = []
    for item in information:
        name = item.get("Name", "")
        ref = item.get("ReferenceNumber")
        value = item.get("Value", {})
        peaks: List[Tuple[float, float]] = []
        if name in FIELDS_TOP5:
            for line in value.get("StringWithMarkup", []):
                parts = line.get("String", "").split()
                if len(parts) == 2:
                    try:
                        mz = float(parts[0]); intensity = float(parts[1])
                        peaks.append((mz, intensity))
                    except ValueError:
                        continue
            if peaks:
                spectra.append({ref: peaks})
        elif name in FIELDS_TOP3:
            nums = value.get("Number", [])
            if len(nums) == 1:
                try:
                    mz_value = float(nums[0])
                    peaks.append((mz_value, 1.0))
                    spectra.append({ref: peaks})
                except ValueError:
                    pass
    return spectra


def find_gc_ms_sections(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the GC-MS information sections safely."""
    def walk(sections):
        for s in sections:
            name = s.get("TOCHeading", "")
            if name and "GC" in name and "MS" in name:
                yield s
            for child in s.get("Section", []) or []:
                yield from walk(child)
    return list(walk(doc.get("Record", {}).get("Section", [])))
