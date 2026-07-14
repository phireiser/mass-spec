"""Reading spectra from the two-tier Parquet store (built by build_parquet_index.py).

The **CAS registry number is the single compound identifier** across the project:
it is present and unique for every store entry, and every dump is named by it. The
store's ``nist_id`` (the NIST Mass Spec No) is retained only as metadata. This
module keys its lookups by CAS, mapping the physical ``nist_id`` join between the
two parquet tiers onto CAS via the index. pyarrow/rdkit are imported lazily so this
module still loads where those packages are absent.
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@lru_cache(maxsize=4)
def _load_parquet_store(parquet_dir: str):
    """Load both tiers once; return (by_inchikey, peaks_by_cas, meta_by_cas), all
    keyed by CAS. Spectra rows are joined to CAS by ``cas`` if present, else via
    the index's ``nist_id`` -> ``cas`` map (current store has no ``cas`` in the
    main tier).

    The InChIKey lookup map is derived from each row's ``isomeric_smiles`` -- the
    store's authoritative structure column -- rather than a stored ``inchikey``
    column (dropped from the store, see build_parquet_index): a persisted key can
    drift from the structure it is meant to identify, so we recompute it. The
    *isomeric* SMILES (not canonical) is used because canonical_smiles is written
    with ``isomericSmiles=False`` and so drops isotope/stereo layers -- which would
    collapse distinct species like benzene and benzene-D6 onto one key."""
    import pyarrow.parquet as pq
    from rdkit import Chem

    root = Path(parquet_dir)
    idx = pq.read_table(root / "index.parquet").to_pandas()
    spec = pq.read_table(root / "spectra.parquet").to_pandas()

    def _s(v) -> str:
        return "" if v is None or (isinstance(v, float) and v != v) else str(v).strip()

    _ik_cache: Dict[str, str] = {}

    def _inchikey(smiles: str) -> str:
        if not smiles:
            return ""
        if smiles not in _ik_cache:
            mol = Chem.MolFromSmiles(smiles)
            _ik_cache[smiles] = Chem.MolToInchiKey(mol) if mol is not None else ""
        return _ik_cache[smiles]

    nist_to_cas: Dict[str, str] = {}
    by_inchikey: Dict[str, str] = {}
    meta_by_cas: Dict[str, dict] = {}
    for row in idx.to_dict("records"):
        cas = _s(row.get("cas"))
        if not cas:
            continue
        nist_to_cas[_s(row.get("nist_id"))] = cas
        ikey = _inchikey(_s(row.get("isomeric_smiles")) or _s(row.get("canonical_smiles")))
        if ikey:
            by_inchikey.setdefault(ikey, cas)
        meta_by_cas.setdefault(cas, {
            "name": row.get("name"), "cas": cas, "formula": row.get("formula"),
            "nominal_mw": row.get("nominal_mw"), "inchikey": ikey,
            "nist_id": _s(row.get("nist_id")),
        })

    has_cas = "cas" in spec.columns
    peaks_by_cas: Dict[str, List[Tuple[float, float]]] = {}
    for rec in spec.to_dict("records"):
        cas = _s(rec.get("cas")) if has_cas else nist_to_cas.get(_s(rec.get("nist_id")), "")
        if not cas:
            continue
        peaks_by_cas[cas] = [(float(x), float(y))
                             for x, y in zip(rec["mz"], rec["intensity"])]
    return by_inchikey, peaks_by_cas, meta_by_cas


def _resolve_cas(smiles: str, by_inchikey: Dict[str, str]) -> Optional[str]:
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return by_inchikey.get(Chem.MolToInchiKey(mol))


def get_cas_by_smiles(smiles: str, parquet_dir: Path) -> Optional[str]:
    """CAS registry number for a molecule by SMILES (via InChIKey), or ``None`` if
    the molecule is not in the store. This is the canonical identifier used to name
    every derivation dump."""
    by_inchikey, _, _ = _load_parquet_store(str(parquet_dir))
    return _resolve_cas(smiles, by_inchikey)


def get_spectra_by_smiles(smiles: str, parquet_dir: Path) -> List[Tuple[float, float]]:
    """Peaks for a molecule by SMILES: canonicalise to InChIKey, resolve to CAS,
    then look up the store. Returns [] if absent."""
    by_inchikey, peaks_by_cas, _ = _load_parquet_store(str(parquet_dir))
    cas = _resolve_cas(smiles, by_inchikey)
    return peaks_by_cas.get(cas, []) if cas is not None else []


def get_record_by_smiles(smiles: str, parquet_dir: Path) -> Dict[str, object]:
    """Full record for a molecule by SMILES: ``{"peaks", "formula", "nominal_mw",
    "name", "cas", "nist_id", "inchikey"}``. Empty dict if not in the store."""
    by_inchikey, peaks_by_cas, meta_by_cas = _load_parquet_store(str(parquet_dir))
    cas = _resolve_cas(smiles, by_inchikey)
    if cas is None:
        return {}
    meta = meta_by_cas.get(cas, {})
    return {"peaks": peaks_by_cas.get(cas, []), **meta}


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "get_cas_by_smiles",
    "get_spectra_by_smiles",
    "get_record_by_smiles",
]
