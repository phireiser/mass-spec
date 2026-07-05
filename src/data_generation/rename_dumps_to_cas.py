"""One-time migration: rename derivation dumps to their CAS registry number.

CAS is the project-wide single identifier (see :mod:`utils.spect_jdx`). Historically
target dumps were named by their human name (``toluene.pkl``) and decoy dumps by
``decoy_<inchikey>.pkl``; this renames every ``.pkl``/``.dmp``/``.done`` in
``fwd/`` and ``bwd/`` to ``<cas>.{pkl,dmp,done}``.

Run it **after** the decoy generation batch finishes (renaming a dump that is still
being written would corrupt it). Idempotent — already-CAS-named dumps are left
alone — and a **dry run by default**; pass ``--apply`` to actually rename.

The stem -> CAS map is built from the definition CSVs (name -> SMILES -> CAS via the
store), so keep the *old* ``decoys*.csv`` in place until this has run. Needs
``pyarrow`` + ``rdkit`` (store lookup), so run inside ``mol-spectro.sif``.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List

from src.data_generation import utils
from src.data_generation.analysis.discrimination import build_decoy_set as bds
from src.project_paths import shared_path

SUFFIXES = (".pkl", ".dmp", ".done")
CAS_RE = re.compile(r"^\d{2,7}-\d{2}-\d$")
DECOY_PREFIX = "decoy_"


def build_resolver(compounds_csv: Path, parquet_dir: Path):
    """Return a ``stem -> CAS`` function.

    Decoy dumps are named ``decoy_<rdkit-inchikey>``, so they resolve through the
    RDKit-InChIKey -> CAS map built exactly as ``build_decoy_set`` built the names
    (recompute the InChIKey from each store row's SMILES, pair with its CAS) -- the
    store's own InChIKey *field* can differ (stereo layers) and must not be used.
    Target dumps are named by their human name; resolve those name -> SMILES -> CAS.
    """
    from rdkit import Chem

    form2structs = bds.load_structures_with_spectra(parquet_dir)
    ik2cas: Dict[str, str] = {s["inchikey"]: s["cas"]
                              for ss in form2structs.values() for s in ss}

    name2cas: Dict[str, str] = {}
    with open(compounds_csv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            name = str(r.get("name", "")).strip()
            smi = str(r.get("smiles", "")).strip()
            if not (name and smi):
                continue
            m = Chem.MolFromSmiles(smi)
            cas = ik2cas.get(Chem.MolToInchiKey(m)) if m else None
            cas = cas or utils.get_cas_by_smiles(smi, parquet_dir)
            if cas:
                name2cas[name] = cas

    def resolve(stem: str):
        if stem.startswith(DECOY_PREFIX):
            return ik2cas.get(stem[len(DECOY_PREFIX):])
        return name2cas.get(stem)

    return resolve


def plan_renames(processed_dir: Path, resolve):
    """Yield (subdir, stem, cas|None) for every dump group that needs renaming."""
    plans = []
    for sub in ("fwd", "bwd"):
        d = processed_dir / sub
        if not d.is_dir():
            continue
        stems = {p.name[: -len(suf)] for suf in SUFFIXES for p in d.glob(f"*{suf}")}
        for stem in sorted(stems):
            if CAS_RE.match(stem):
                continue  # already migrated
            plans.append((sub, stem, resolve(stem)))
    return plans


def main() -> None:
    ap = argparse.ArgumentParser(description="Rename derivation dumps to CAS")
    ap.add_argument("--processed-dir", default=str(shared_path("PROCESSED_DIR_REL")))
    ap.add_argument("--compounds-csv", default=str(shared_path("CSV_PATH_REL")))
    ap.add_argument("--spectra-folder", default=str(shared_path("PARQUET_DIR_REL")))
    ap.add_argument("--apply", action="store_true", help="Actually rename (default: dry run)")
    args = ap.parse_args()

    processed_dir = Path(args.processed_dir)
    parquet_dir = Path(args.spectra_folder)

    resolve = build_resolver(Path(args.compounds_csv), parquet_dir)
    plans = plan_renames(processed_dir, resolve)

    renamed = skipped_unknown = skipped_exists = 0
    for sub, stem, cas in plans:
        d = processed_dir / sub
        if cas is None:
            print(f"  SKIP (no CAS): {sub}/{stem}")
            skipped_unknown += 1
            continue
        # Collision: the CAS dump already exists (e.g. a decoy that is also a target).
        if any((d / (cas + suf)).exists() for suf in SUFFIXES):
            print(f"  SKIP (CAS dump exists): {sub}/{stem} -> {cas}")
            skipped_exists += 1
            continue
        for suf in SUFFIXES:
            src = d / (stem + suf)
            if src.exists():
                dst = d / (cas + suf)
                print(f"  {'RENAME' if args.apply else 'DRY'} {sub}/{stem}{suf} -> {cas}{suf}")
                if args.apply:
                    src.rename(dst)
        renamed += 1

    action = "renamed" if args.apply else "would rename"
    print(f"\n{action} {renamed} dump groups; "
          f"skipped {skipped_unknown} unknown, {skipped_exists} already-present CAS.")
    if not args.apply:
        print("Dry run — re-run with --apply to perform the renames.")


if __name__ == "__main__":
    main()
