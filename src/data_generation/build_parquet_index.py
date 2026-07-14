#!/usr/bin/env python3
"""Build a two-tier Parquet store for NIST EI mass spectra.

Tier 1 -- ``spectra.parquet`` (main store, keyed by ``nist_id``): the actual
spectral payload, one row per spectrum. Holds the parsed peak arrays plus the
verbatim JCAMP-DX text so the single file is both archive and dataset.

Tier 2 -- ``index.parquet`` (side index, one row per ``nist_id``): the rich
lookup/query surface. Molecule identity (InChIKey, canonical/isomeric SMILES,
InChI), identifiers (CAS, name), physicochemical attributes, and a Morgan
(ECFP4) fingerprint packed to bytes for Tanimoto similarity / substructure
screening.

Lookup flow ("find by SMILES"): canonicalise the query SMILES with RDKit ->
InChIKey, then filter the side index on ``inchikey`` (predicate pushdown via
DuckDB/Polars/pyarrow), and join to the main store on ``nist_id``.

Fingerprints are stored as ``np.packbits`` of the 2048-bit vector (256 bytes),
portable to numpy/FAISS; helper ``unpack_fp`` reconstructs the bit array.

Fetches the WHOLE NIST WebBook up to a max molecular weight (``--max-mw``):
enumerate species via the MW search, then per species download the JCAMP
spectrum + the MOL structure (``Str2File``). Resumable.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem import rdinchi

MORGAN_RADIUS = 2
MORGAN_BITS = 2048
_MORGAN_GEN = rdFingerprintGenerator.GetMorganGenerator(
    radius=MORGAN_RADIUS, fpSize=MORGAN_BITS
)


# ---------------------------------------------------------------- JDX parsing

def parse_jdx_text(raw: str) -> Tuple[Dict[str, str], List[float], List[float]]:
    """Return (header, mz, intensity) for JCAMP-DX mass-spectrum text."""
    header: Dict[str, str] = {}
    mz: List[float] = []
    inten: List[float] = []
    in_peaks = False
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("##PEAK"):
            in_peaks = True
            continue
        if line.startswith("##END"):
            break
        if not in_peaks:
            if line.startswith("##"):
                key, sep, val = line[2:].partition("=")
                if sep:
                    header[key.strip().lstrip("$").upper()] = val.strip()
            continue
        for token in line.split():
            try:
                x, y = token.split(",")
                mz.append(float(x))
                inten.append(float(y))
            except ValueError:
                continue
    return header, mz, inten


# ------------------------------------------------------------ RDKit features

def pack_fp(mol: Chem.Mol) -> bytes:
    """Morgan ECFP4 bit vector -> packed bytes (256 bytes for 2048 bits)."""
    fp = _MORGAN_GEN.GetFingerprint(mol)
    arr = np.zeros((MORGAN_BITS,), dtype=np.uint8)
    from rdkit.DataStructs import ConvertToNumpyArray

    ConvertToNumpyArray(fp, arr)
    return np.packbits(arr).tobytes()


def unpack_fp(blob: bytes, n_bits: int = MORGAN_BITS) -> np.ndarray:
    """Inverse of pack_fp: bytes -> uint8 bit array of length n_bits."""
    return np.unpackbits(np.frombuffer(blob, dtype=np.uint8))[:n_bits]


def mol_to_inchi(mol: Chem.Mol) -> str:
    """``Chem.MolToInchi`` but with any InChI-library diagnostic re-emitted with
    an explicit ``[RDKit InChI]`` tag instead of RDKit's untagged stderr line.

    Structures pulled from the NIST WebBook routinely trip normalisation
    warnings such as "Omitted undefined stereo" or "Charges were rearranged".
    These originate in the IUPAC InChI C library (via RDKit), not in our fetch
    code, so we mark their provenance to keep the build log unambiguous. The
    low-level ``rdinchi.MolToInchi`` returns the message rather than printing it,
    letting us prefix it ourselves. ``/AuxNone`` mirrors ``Chem.MolToInchi``.
    """
    inchi, _retcode, message, _logs, _aux = rdinchi.MolToInchi(mol, "/AuxNone")
    if message:
        print(f"[RDKit InChI] {message}", file=sys.stderr, flush=True)
    return inchi


def features_from_mol(mol: Chem.Mol) -> Dict[str, object]:
    """Derive molecule-identity + physicochemical columns from an RDKit mol."""
    inchi = mol_to_inchi(mol)
    return {
        # Derive the key from the InChI we already built (identical to
        # Chem.MolToInchiKey), falling back to the mol if generation failed.
        "inchikey": Chem.InchiToInchiKey(inchi) if inchi else Chem.MolToInchiKey(mol),
        "inchi": inchi,
        "canonical_smiles": Chem.MolToSmiles(mol, isomericSmiles=False),
        "isomeric_smiles": Chem.MolToSmiles(mol, isomericSmiles=True),
        "formula": rdMolDescriptors.CalcMolFormula(mol),
        "exact_mw": float(Descriptors.ExactMolWt(mol)),
        "avg_mw": float(Descriptors.MolWt(mol)),
        "n_heavy_atoms": mol.GetNumHeavyAtoms(),
        "n_rings": rdMolDescriptors.CalcNumRings(mol),
        "n_aromatic_rings": rdMolDescriptors.CalcNumAromaticRings(mol),
        "n_rotatable_bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "fraction_csp3": float(rdMolDescriptors.CalcFractionCSP3(mol)),
        "tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
        "clogp": float(Descriptors.MolLogP(mol)),
        "morgan_fp": pack_fp(mol),
    }


# ---------------------------------------------------- NIST WebBook catalog I/O

NIST_CGI = "https://webbook.nist.gov/cgi/cbook.cgi"
_ID_LINK = re.compile(r'<a href="/cgi/cbook\.cgi\?ID=(C\d+)[^"]*">')
_INCHI_LINK = re.compile(r'/cgi/inchi/(InChI%3D[^"\'>]+)')


def _new_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "mol-thesis-nist-catalog/1.0"})
    return s


def _get(session: requests.Session, params: dict, retries: int = 5) -> Optional[str]:
    """GET with retry + NIST rate-limit backoff. Returns text or None."""
    for attempt in range(retries):
        try:
            resp = session.get(NIST_CGI, params=params, timeout=30)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            wait = 2 * (attempt + 1)
            print(f"    request error ({exc}); retry in {wait}s", flush=True)
            time.sleep(wait)
            continue
        if "Rate limit exceeded" in resp.text:
            wait = 30 * (attempt + 1)
            print(f"    NIST rate-limited; backing off {wait}s", flush=True)
            time.sleep(wait)
            continue
        return resp.text
    return None


def enumerate_catalog(session: requests.Session, mw_start: int, max_mw: int,
                      delay: float) -> List[str]:
    """Return the WebBook IDs (C#####) of every species with a mass spectrum in
    ``[mw_start, max_mw]``. The MW search matches within +/-0.5, so stepping the
    integer value by 1 is gap-free."""
    seen: Dict[str, None] = {}
    for mw in range(mw_start, max_mw + 1):
        text = _get(session, {"Value": str(mw), "VType": "MW", "Units": "SI", "cMS": "on"})
        if text is None:
            print(f"  MW={mw}: giving up after retries", flush=True)
            continue
        if "matching species were found" in text:
            found = _ID_LINK.findall(text)
        else:  # single-species redirect page: IDs all point at the one species
            hits = _ID_LINK.findall(text)
            found = [max(set(hits), key=hits.count)] if hits else []
        for cid in found:
            seen.setdefault(cid, None)
        print(f"  MW={mw:>4}  species so far={len(seen):>6}", flush=True)
        time.sleep(delay)
    return list(seen)


def fetch_jcamp_by_id(session: requests.Session, webbook_id: str) -> Optional[str]:
    """Download the primary EI spectrum for a WebBook ID as JCAMP-DX text."""
    text = _get(session, {"JCAMP": webbook_id, "Index": "0", "Type": "Mass"})
    if text and ("##TITLE=" in text or "##JCAMP-DX=" in text):
        return text
    return None


# Known NIST WebBook structure-resolution errors: for these species the WebBook
# structure endpoints (Str2File / InChI-on-page) return the WRONG molecule, so the
# built store would carry a foreign structure (inchikey/smiles/fingerprint) against
# a correct spectrum + name. Map the WebBook ID to a correct SMILES to override the
# fetch. Keep this list in sync with any structure fixes applied to the built store.
STRUCTURE_OVERRIDES: Dict[str, str] = {
    # C119653 (Isoquinoline) resolves to quinoline's MOL; supply real isoquinoline.
    "C119653": "c1ccc2cnccc2c1",
}


def fetch_structure(session: requests.Session, webbook_id: str) -> Optional[Chem.Mol]:
    """Resolve a species' structure: a curated override (for known WebBook errors)
    takes precedence, then the MOL file via ``Str2File`` (preferred), with an
    InChI-from-page fallback. Returns an RDKit mol or None."""
    override = STRUCTURE_OVERRIDES.get(webbook_id)
    if override:
        mol = Chem.MolFromSmiles(override)
        if mol is not None:
            return mol
    mol_block = _get(session, {"Str2File": webbook_id})
    if mol_block:
        mol = Chem.MolFromMolBlock(mol_block)
        if mol is not None:
            return mol
    page = _get(session, {"ID": webbook_id, "Mask": "200"})
    if page:
        m = _INCHI_LINK.search(page)
        if m:
            return Chem.MolFromInchi(unquote(m.group(1)))
    return None


# ------------------------------------------------------------ Arrow schemas

# CAS is the project-wide single identifier (primary key); nist_id (the NIST Mass
# Spec No) is retained as metadata for provenance.
SPECTRA_SCHEMA = pa.schema([
    ("cas", pa.string()),
    ("nist_id", pa.string()),
    ("mz", pa.list_(pa.float32())),
    ("intensity", pa.list_(pa.float32())),
    ("n_peaks", pa.int32()),
    ("base_peak_mz", pa.float32()),
    ("jdx_raw", pa.string()),
])

INDEX_SCHEMA = pa.schema([
    ("cas", pa.string()),
    ("nist_id", pa.string()),
    ("webbook_id", pa.string()),
    ("canonical_smiles", pa.string()),
    ("isomeric_smiles", pa.string()),
    ("inchi", pa.string()),
    ("cas", pa.string()),
    ("name", pa.string()),
    ("formula", pa.string()),
    ("nominal_mw", pa.int32()),
    ("exact_mw", pa.float64()),
    ("avg_mw", pa.float64()),
    ("n_heavy_atoms", pa.int32()),
    ("n_rings", pa.int32()),
    ("n_aromatic_rings", pa.int32()),
    ("n_rotatable_bonds", pa.int32()),
    ("fraction_csp3", pa.float64()),
    ("tpsa", pa.float64()),
    ("clogp", pa.float64()),
    ("jcamp_url", pa.string()),
    ("morgan_fp", pa.binary()),
])


# ------------------------------------------------------------ builders

def _spectrum_rows(nist_id: str, header: Dict[str, str], mz: List[float],
                   inten: List[float], raw: str, mol: Optional[Chem.Mol],
                   fallback_name: str) -> Tuple[dict, dict]:
    """Build the (main-store, side-index) row pair for one spectrum. ``mol`` may
    be None (structure unresolved): the spectrum + header metadata are still
    kept, with structure/fingerprint columns left null."""
    feats = features_from_mol(mol) if mol is not None else {}
    base_mz = float(mz[int(np.argmax(inten))]) if inten else 0.0
    cas = header.get("CAS REGISTRY NO", "")
    webbook_id = f"C{cas.replace('-', '')}" if cas else ""
    spec_row = {
        "cas": cas,
        "nist_id": nist_id,
        "inchikey": feats.get("inchikey"),
        "mz": [float(x) for x in mz],
        "intensity": [float(y) for y in inten],
        "n_peaks": len(mz),
        "base_peak_mz": base_mz,
        "jdx_raw": raw,
    }
    idx_row = {
        "nist_id": nist_id,
        "webbook_id": webbook_id,
        "cas": cas,
        "name": header.get("TITLE", fallback_name),
        "nominal_mw": int(float(header.get("MW", "0") or 0)),
        "jcamp_url": f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP={webbook_id}"
                     "&Index=0&Type=Mass",
        **feats,
    }
    return spec_row, idx_row


def _cid_to_cas(cid: str) -> str:
    """C74828 -> 74-82-8; '' if the digits can't form a CAS."""
    digits = cid[1:]
    return f"{digits[:-3]}-{digits[-3:-1]}-{digits[-1]}" if len(digits) >= 4 else ""


def build_from_catalog(max_mw: int, out_dir: Path, delay: float = 1.0,
                       mw_start: int = 1, checkpoint_every: int = 300) -> None:
    """Fetch the entire NIST WebBook EI catalog up to ``max_mw`` into the Parquet
    store. Enumerates species by MW, then per species downloads the JCAMP
    spectrum and the MOL structure. Resumable: an existing store is loaded and
    already-fetched species (by ``webbook_id``) are skipped."""
    session = _new_session()
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_path = out_dir / "spectra.parquet"
    idx_path = out_dir / "index.parquet"

    spec_rows: List[dict] = []
    idx_rows: List[dict] = []
    done: set = set()
    if spec_path.exists() and idx_path.exists():
        prev_spec = pq.read_table(spec_path).to_pandas()
        prev_idx = pq.read_table(idx_path).to_pandas()
        for r in prev_spec.to_dict("records"):
            r["mz"] = [float(x) for x in r["mz"]]
            r["intensity"] = [float(x) for x in r["intensity"]]
            spec_rows.append(r)
        if "webbook_id" not in prev_idx.columns:
            # store written before the webbook_id column existed; derive it from CAS
            prev_idx["webbook_id"] = prev_idx["cas"].fillna("").map(
                lambda c: f"C{c.replace('-', '')}" if c else "")
        idx_rows = prev_idx.to_dict("records")
        done = {w for w in prev_idx["webbook_id"].tolist() if w}
        print(f"Resuming: {len(done)} species already in store")

    print(f"Enumerating NIST species with MW in [{mw_start}, {max_mw}] ...")
    ids = enumerate_catalog(session, mw_start, max_mw, delay)
    todo = [c for c in ids if c not in done]
    print(f"{len(ids)} species enumerated; {len(todo)} still to fetch")

    failed: List[Tuple[str, str]] = []
    for i, wid in enumerate(todo, 1):
        jcamp = fetch_jcamp_by_id(session, wid)
        time.sleep(delay)
        if not jcamp:
            failed.append((wid, "no spectrum"))
            continue
        header, mz, inten = parse_jdx_text(jcamp)
        header.setdefault("CAS REGISTRY NO", _cid_to_cas(wid))
        mol = fetch_structure(session, wid)
        time.sleep(delay)
        nist_id = header.get("NIST MASS SPEC NO") or wid.lstrip("C")
        spec_row, idx_row = _spectrum_rows(nist_id, header, mz, inten, jcamp, mol, wid)
        spec_rows.append(spec_row)
        idx_rows.append(idx_row)

        if i % 25 == 0 or i == len(todo):
            print(f"  [{i}/{len(todo)}] {wid} {header.get('TITLE', '?')[:28]:<28} "
                  f"struct={'y' if mol else 'n'} total={len(spec_rows)}", flush=True)
        if checkpoint_every and i % checkpoint_every == 0:
            _write(spec_rows, SPECTRA_SCHEMA, spec_path, sort_key="nist_id")
            _write(idx_rows, INDEX_SCHEMA, idx_path, sort_key="cas")

    _write(spec_rows, SPECTRA_SCHEMA, spec_path, sort_key="nist_id")
    _write(idx_rows, INDEX_SCHEMA, idx_path, sort_key="inchikey")
    n_struct = sum(1 for r in idx_rows if r.get("inchikey"))
    print(f"\nDone. {len(spec_rows)} spectra in store "
          f"({n_struct} with structure), {len(failed)} failed to download.")


def _write(rows: List[dict], schema: pa.Schema, path: Path, sort_key: str) -> None:
    if not rows:
        raise SystemExit(f"no rows to write for {path}")
    df = pd.DataFrame(rows).sort_values(sort_key, na_position="last").reset_index(drop=True)
    # reorder to schema field order, filling any missing
    cols = [f.name for f in schema]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    table = pa.Table.from_pandas(df[cols], schema=schema, preserve_index=False)
    pq.write_table(table, path, compression="zstd", version="2.6")
    print(f"  -> {path.name}: {table.num_rows} rows, {path.stat().st_size/1024:.1f} KiB "
          f"(sorted by {sort_key})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-mw", type=int, default=1000,
                    help="molecular-weight cutoff (fetch every species up to this MW)")
    ap.add_argument("--mw-start", type=int, default=1,
                    help="lower molecular-weight bound")
    ap.add_argument("--out-dir", default="outputs/nist_spectra")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="seconds between NIST requests; be polite / avoid rate limits")
    args = ap.parse_args()

    build_from_catalog(args.max_mw, Path(args.out_dir), args.delay, args.mw_start)


if __name__ == "__main__":
    main()
