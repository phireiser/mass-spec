"""
Audit: consistency between data/compounds.csv structures and the NIST Parquet store.

Motivated by two confirmed structure-resolution bugs (isoquinoline, then salicylic
acid): a compounds.csv SMILES can silently resolve to a store record for a
*different* molecule, so MOD fragments one structure while being scored against
another's spectrum. Those are invisible unless you look for them.

Three objective checks (no network, no name->structure database needed):

  1. NO RECORD      -- the SMILES has no row in the store, so the molecule is
                       silently dropped from every scoring run.
  2. FORMULA/MW     -- the formula (and nominal mass) computed from the
                       compounds.csv SMILES disagrees with the store record's
                       formula / nominal_mw. Catches gross structure errors.
  3. CAS COLLISION  -- two or more *different* compounds.csv names resolve to the
                       same store CAS, i.e. they are being scored against the same
                       spectrum. (The ~113 known same-structure collisions.)

Note the limitation: an isomer swap that preserves the formula (exactly the
salicylic case, C7H6O3 either way) is NOT caught by check 2. Check 3 catches it
only if both isomers are in compounds.csv. Formula-preserving isomer errors need an
external name->structure reference, so they are reported here only when they also
trip 1 or 3; treat this audit as a lower bound on the true error count.

Run inside mol-spectro.sif.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from src.data_generation import utils
from src.project_paths import shared_path

from rdkit import Chem
from rdkit.Chem.rdMolDescriptors import CalcMolFormula


def _norm_formula(f: str) -> str:
    """Normalise 'C3 H6 O' / 'C3H6O' to a comparable canonical token string."""
    return "".join(str(f or "").split()).replace("+", "").replace("-", "").strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compounds-csv", default=str(shared_path("CSV_PATH_REL")))
    ap.add_argument("--spectra-folder", default=str(shared_path("PARQUET_DIR_REL")))
    args = ap.parse_args()

    parquet_dir = Path(args.spectra_folder)
    with open(args.compounds_csv, newline="", encoding="utf-8") as f:
        rows = [(str(r["name"]).strip(), str(r["smiles"]).strip()) for r in csv.DictReader(f)]

    no_record, formula_bad, ok = [], [], 0
    cas_to_names = defaultdict(list)

    for name, smi in rows:
        rec = utils.get_record_by_smiles(smi, parquet_dir)
        if not rec:
            no_record.append((name, smi))
            continue
        ok += 1
        cas = rec.get("cas")
        if cas:
            cas_to_names[str(cas)].append((name, smi, rec.get("name")))

        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            formula_bad.append((name, smi, "UNPARSEABLE", rec.get("formula"), rec.get("name")))
            continue
        f_csv = _norm_formula(CalcMolFormula(mol))
        f_store = _norm_formula(rec.get("formula"))
        if f_store and f_csv != f_store:
            formula_bad.append((name, smi, f_csv, f_store, rec.get("name")))

    collisions = {c: v for c, v in cas_to_names.items() if len({n for n, _, _ in v}) > 1}

    print(f"=== compounds.csv entries: {len(rows)}  |  resolved to a store record: {ok} ===")

    print(f"\n--- [1] NO RECORD in store ({len(no_record)}) : silently dropped from scoring ---")
    for name, smi in no_record:
        print(f"  {name:32s} {smi}")

    print(f"\n--- [2] FORMULA MISMATCH ({len(formula_bad)}) : csv structure != store spectrum ---")
    for name, smi, f_csv, f_store, rec_name in formula_bad:
        print(f"  {name:28s} csv={f_csv:12s} store={f_store:12s} storeName={rec_name!r}")
        print(f"      {smi}")

    print(f"\n--- [3] CAS COLLISIONS ({len(collisions)}) : distinct names -> one spectrum ---")
    for cas, v in sorted(collisions.items(), key=lambda kv: -len(kv[1])):
        names = sorted({n for n, _, _ in v})
        print(f"  CAS {cas:14s} storeName={v[0][2]!r}")
        for n, s, _ in sorted(v):
            print(f"      {n:28s} {s}")
        del names

    print("\n=== SUMMARY ===")
    print(f"  no record      : {len(no_record)}")
    print(f"  formula mismatch: {len(formula_bad)}")
    print(f"  cas collisions : {len(collisions)} (covering "
          f"{sum(len({n for n,_,_ in v}) for v in collisions.values())} names)")


if __name__ == "__main__":
    main()
