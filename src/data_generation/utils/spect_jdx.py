"""Reading spectra from the two-tier Parquet store (built by build_parquet_index.py).

Main store ``spectra.parquet`` (keyed nist_id) + side index
``index.parquet`` (keyed inchikey). pyarrow/rdkit are imported lazily so this
module still loads where those packages are absent (e.g. a container built before
they were added).
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple


@lru_cache(maxsize=4)
def _load_parquet_store(parquet_dir: str):
    """Load both tiers once; return (by_inchikey, peaks_by_id, meta_by_id)."""
    import pyarrow.parquet as pq

    root = Path(parquet_dir)
    idx = pq.read_table(root / "index.parquet").to_pandas()
    spec = pq.read_table(root / "spectra.parquet").to_pandas()

    by_inchikey: Dict[str, str] = {}
    for key, nid in zip(idx["inchikey"], idx["nist_id"]):
        if key:
            by_inchikey.setdefault(key, nid)
    peaks_by_id = {
        nid: [(float(x), float(y)) for x, y in zip(mz, inten)]
        for nid, mz, inten in zip(spec["nist_id"], spec["mz"], spec["intensity"])
    }
    meta_by_id = {
        row["nist_id"]: {
            "name": row["name"], "cas": row["cas"], "formula": row["formula"],
            "nominal_mw": row["nominal_mw"], "inchikey": row["inchikey"],
        }
        for row in idx.to_dict("records")
    }
    return by_inchikey, peaks_by_id, meta_by_id


def _resolve_id(smiles: str, by_inchikey: Dict[str, str]):
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return by_inchikey.get(Chem.MolToInchiKey(mol))


def get_spectra_by_smiles(smiles: str, parquet_dir: Path) -> List[Tuple[float, float]]:
    """Peaks for a molecule by SMILES: canonicalise to InChIKey, then look up the
    side index. Handles any valid SMILES spelling. Returns [] if absent."""
    by_inchikey, peaks_by_id, _ = _load_parquet_store(str(parquet_dir))
    nid = _resolve_id(smiles, by_inchikey)
    return peaks_by_id.get(nid, []) if nid is not None else []


def get_record_by_smiles(smiles: str, parquet_dir: Path) -> Dict[str, object]:
    """Full record for a molecule by SMILES: ``{"peaks", "formula", "nominal_mw",
    "name", "cas", "inchikey"}``. Empty dict if the molecule is not in the store."""
    by_inchikey, peaks_by_id, meta_by_id = _load_parquet_store(str(parquet_dir))
    nid = _resolve_id(smiles, by_inchikey)
    if nid is None:
        return {}
    meta = meta_by_id.get(nid, {})
    return {"peaks": peaks_by_id.get(nid, []), **meta}


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "get_spectra_by_smiles",
    "get_record_by_smiles",
]
