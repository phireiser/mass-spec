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
    # C69727 (Salicylic acid, CAS 69-72-7) resolves to 3-hydroxybenzoic acid
    # (meta, O=C(O)c1cccc(O)c1) instead of the 2-hydroxy (ortho) isomer. The
    # spectrum is genuinely salicylic's -- base peak m/z 120 is the ortho-effect
    # water loss, which the meta isomer physically cannot do -- so the mismatch made
    # that base peak permanently unexplainable. Supply real salicylic acid.
    "C69727": "O=C(O)c1ccccc1O",
    # C109977 (Pyrrole, CAS 109-97-7) resolves to 3H-pyrrole (C1=CN=CC1, a
    # NON-aromatic imine with an sp3 CH2), not aromatic 1H-pyrrole. Same C4H5N
    # formula, so the audit's formula check cannot see it. It matters here because
    # the forward model protects an aromatic ring (bonds ride through as the inert
    # term e(ar)) while it happily shreds the non-aromatic isomer, so the wrong
    # structure would fragment along bonds real pyrrole does not have. Supply real
    # aromatic pyrrole.
    "C109977": "c1cc[nH]c1",
    # C75478 (Iodoform / "Methane, triiodo-", CAS 75-47-8) resolves to a
    # hypervalent-iodine junk MOL (C[IH](I)(I)I, RDKit formula CH4I4, nominal 524)
    # -- a typo'd SMILES, not the real CHI3 (nominal 394). The stored nominal_mw
    # (394) and spectrum are genuinely iodoform's, so MOD was fragmenting a 524-Da
    # phantom and the surplus mass showed up as supra-parent fragments with zero
    # fusion edges. Supply real iodoform.
    "C75478": "C(I)(I)I",
    # C127184 (Tetrachloroethylene, CAS 127-18-4) resolves to a 4-carbon
    # tetrachloro-1,3-butadiene (ClC=C(Cl)C(Cl)=CCl, C4H2Cl4, nominal 190) instead
    # of perchloroethylene C2Cl4 (nominal 164). Same supra-parent-with-no-fusion
    # signature. Supply real tetrachloroethylene.
    "C127184": "ClC(Cl)=C(Cl)Cl",
    # --- 2026-07-22 batch: 34 more WebBook structures whose fetched MOL disagrees
    # with the record's NIST nominal_mw (audit check [2b]). Each SMILES is the
    # PubChem canonical parent for the record's CAS, verified so its nominal mass
    # equals the store nominal_mw (shown in the trailing comment as formula, mass).
    "C541059": "C[Si]1(C)O[Si](C)(C)O[Si](C)(C)O1",  # hexamethylcyclotrisiloxane (C6H18O3Si3, 222)
    "C52904": "NC(CS)C(=O)O",  # cysteine (C3H7NO2S, 121)
    "C70473": "NC(=O)CC(N)C(=O)O",  # asparagine (C4H8N2O3, 132)
    "C56859": "NC(=O)CCC(N)C(=O)O",  # glutamine (C5H10N2O3, 146)
    "C74793": "NC(N)=NCCCC(N)C(=O)O",  # arginine (C6H14N4O2, 174)
    "C533675": "OCC1OC(O)CC1O",  # deoxyribose (C5H10O4, 134)
    "C60333": "CCCCCC=CCC=CCCCCCCCC(=O)O",  # linoleic_acid (C18H32O2, 280)
    "C98920": "NC(=O)c1cccnc1",  # nicotinamide (C6H6N2O, 122)
    "C83885": "Cc1cc2nc3c(=O)[nH]c(=O)nc-3n(CC(O)C(O)C(O)CO)c2cc1C",  # riboflavin (C17H20N4O6, 376)
    "C50817": "O=C1OC(C(O)CO)C(O)=C1O",  # ascorbic_acid (C6H8O6, 176)
    "C57885": "CC(C)CCCC(C)C1CCC2C3CC=C4CC(O)CCC4(C)C3CCC12C",  # cholesterol (C27H46O, 386)
    "C73405": "Nc1nc2nc[nH]c2c(=O)[nH]1",  # guanine (C5H5N5O, 151)
    "C58617": "Nc1ncnc2c1ncn2C1OC(CO)C(O)C1O",  # adenosine (C10H13N5O4, 267)
    "C71443": "NCCCNCCCCNCCCN",  # spermine (C10H26N4, 202)
    "C51616": "NCCc1ccc(O)c(O)c1",  # dopamine (C8H11NO2, 153)
    "C51672": "NCCc1ccc(O)cc1",  # tyramine (C8H11NO, 137)
    "C73314": "COc1ccc2[nH]cc(CCNC(C)=O)c2c1",  # melatonin (C13H16N2O2, 232)
    "C58220": "CC12CCC(=O)C=C1CCC1C2CCC2(C)C(O)CCC12",  # testosterone (C19H28O2, 288)
    "C50282": "CC12CCC3c4ccc(O)cc4CCC3C1CCC2O",  # estradiol (C18H24O2, 272)
    "C53167": "CC12CCC3c4ccc(O)cc4CCC3C1CCC2=O",  # estrone (C18H22O2, 270)
    "C57830": "CC(=O)C1CCC2C3CCC4=CC(=O)CCC4(C)C3CCC12C",  # progesterone (C21H30O2, 314)
    "C50237": "CC12CCC(=O)C=C1CCC1C2C(O)CC2(C)C1CCC2(O)C(=O)CO",  # cortisol (C21H30O5, 362)
    "C52391": "CC12CCC(=O)C=C1CCC1C2C(O)CC2(C=O)C(C(=O)CO)CCC12",  # aldosterone (C21H28O5, 360)
    "C53430": "CC12CCC3C(CC=C4CC(O)CCC43C)C1CCC2=O",  # dehydroepiandrosterone (C19H28O2, 288)
    "C58855": "O=C(O)CCCCC1SCC2NC(=O)NC21",  # biotin (C10H16N2O3S, 244)
    "C7235407": "CC(C=CC=C(C)C=CC1=C(C)CCCC1(C)C)=CC=CC=C(C)C=CC=C(C)C=CC1=C(C)CCCC1(C)C",  # beta_carotene (C40H56, 536)
    "C97530": "C=CCc1ccc(O)c(OC)c1",  # eugenol (C10H12O2, 164)
    "C56757": "O=C(NC(CO)C(O)c1ccc([N+](=O)[O-])cc1)C(Cl)Cl",  # chloramphenicol (C11H12Cl2N2O5, 322)
    "C126078": "COC1=CC(=O)CC(C)C12Oc1c(Cl)c(OC)cc(OC)c1C2=O",  # griseofulvin (C17H17ClO6, 352)
    "C1162658": "COc1cc2c(c3oc(=O)c4c(c13)CCC4=O)C1C=COC1O2",  # aflatoxin_B1 (C17H12O6, 312)
    "C51343": "CN1C2CC(OC(=O)C(CO)c3ccccc3)CC1C1OC12",  # scopolamine (C17H21NO4, 303)
    "C51558": "CN1C2CCC1CC(OC(=O)C(CO)c1ccccc1)C2",  # atropine (C17H23NO3, 289)
    "C76573": "COc1ccc2c3c1OC1C(O)C=CC4C(C2)N(C)CCC341",  # codeine (C18H21NO3, 299)
    "C5392405": "CC(C)=CCCC(C)=CC=O",  # citral (C10H16O, 152)
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
    ap.add_argument("--out-dir", default="data/outputs/nist_spectra")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="seconds between NIST requests; be polite / avoid rate limits")
    args = ap.parse_args()

    build_from_catalog(args.max_mw, Path(args.out_dir), args.delay, args.mw_start)


if __name__ == "__main__":
    main()
