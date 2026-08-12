"""Build the decoy forward-generation input for the Phase-1 discrimination batch.

The oracle library-match baseline (``discriminate``) uses each decoy's *measured*
spectrum. The forward half of Phase 1 instead scores each candidate structure by
``cosine(observed_true, MØD_predicted(candidate))``, so it needs a MØD forward DG
dump for every decoy structure. This module collects the unique same-formula decoy
structures for the target set and writes a ``name,smiles,category`` CSV in the exact
format ``run/hpc/data_gen.sh`` consumes, sorted easy->hard by heavy-atom count so the
generation batch can be staged in waves and gated on the observed cost.

Decoys that already have a forward dump (a target that is another target's
same-formula isomer) are skipped. Needs ``pyarrow`` + ``rdkit``, so run inside
``mol-spectro.sif``.

Usage (inside the container):
  python -m src.data_generation.analysis.discrimination.build_decoy_set \
      --out-dir data --max-heavy 9        # wave 1 (<=9 heavy) + full set + wave 2
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

from src.project_paths import shared_path


def _str(v) -> str:
    return "" if v is None or (isinstance(v, float) and v != v) else str(v).strip()


def load_structures_with_spectra(parquet_dir: Path):
    """Map RDKit molecular formula -> list of distinct decoy-candidate structures.

    Structures are keyed by the **RDKit-recomputed InChIKey** from the stored
    SMILES, not the store's ``inchikey`` field. NIST labels isotopologues
    (Methanol-D4, ...) with the unlabelled formula but strips the isotope from the
    SMILES, so several store rows collapse to one real structure -- deduping on the
    recomputed key removes those and the name collisions they cause. Rows with an
    explicit isotope in the SMILES, or whose RDKit formula disagrees with the store
    formula, are dropped as unsuitable same-formula decoys.

    Each entry carries ``cas`` (the first row's) **and** ``cas_all`` (every CAS the store
    files under that structure). Both are needed: the store has same-structure rows under
    distinct registry numbers, and a dump is named by whichever CAS
    ``utils.get_cas_by_smiles`` returns -- not necessarily the first row seen here. Keying
    dump lookup on ``cas`` alone made the forward scorer miss 32 decoys that were on disk
    the whole time, which silently inflates top-1 (an unscored decoy cannot outrank the
    true structure).
    """
    import pyarrow.parquet as pq
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors

    idx = pq.read_table(parquet_dir / "index.parquet").to_pandas()
    spec_ids = set(pq.read_table(parquet_dir / "spectra.parquet").to_pandas()["nist_id"])

    form2structs: Dict[str, List[dict]] = defaultdict(list)
    seen: Dict[str, dict] = {}
    for r in idx.to_dict("records"):
        if r["nist_id"] not in spec_ids:
            continue
        store_formula = _str(r.get("formula"))
        smiles = _str(r.get("canonical_smiles")) or _str(r.get("isomeric_smiles"))
        if not smiles:
            continue
        mol = Chem.MolFromSmiles(smiles)
        if mol is None or any(a.GetIsotope() for a in mol.GetAtoms()):
            continue
        rd_formula = rdMolDescriptors.CalcMolFormula(mol)
        if store_formula and rd_formula.rstrip("+-") != store_formula:
            continue  # mislabelled / isotopologue with shifted true mass
        cas = _str(r.get("cas"))
        if not cas:
            continue  # CAS is the identifier every dump is named by; no CAS => unusable
        key = Chem.MolToInchiKey(mol)
        if key in seen:
            aliases = seen[key]["cas_all"]      # same structure, second registry number
            if cas not in aliases:
                aliases.append(cas)
            continue
        entry = {
            "inchikey": key, "cas": cas, "cas_all": [cas], "smiles": Chem.MolToSmiles(mol),
            "formula": rd_formula, "name": _str(r.get("name")),
            "nheavy": mol.GetNumHeavyAtoms(),
        }
        seen[key] = entry
        form2structs[rd_formula].append(entry)
    return dict(form2structs)


def main() -> None:
    from rdkit import Chem

    ap = argparse.ArgumentParser(description="Build the Phase-1 decoy generation CSV")
    ap.add_argument("--spectra-folder", default=str(shared_path("PARQUET_DIR_REL")))
    ap.add_argument("--compounds-csv", default=str(shared_path("CSV_PATH_REL")))
    ap.add_argument("--fwd-dir", default=str(shared_path("FWD_DIR_REL")))
    ap.add_argument("--out-dir", default=str(shared_path("DATA_DIR_REL")))
    ap.add_argument("--max-heavy", type=int, default=9,
                    help="Wave-1 cutoff: structures with <= this many heavy atoms")
    args = ap.parse_args()

    parquet_dir = Path(args.spectra_folder)
    out_dir = Path(args.out_dir)
    form2structs = load_structures_with_spectra(parquet_dir)
    key2struct = {s["inchikey"]: s for ss in form2structs.values() for s in ss}

    with open(args.compounds_csv, newline="", encoding="utf-8") as f:
        targets = {str(r["name"]).strip(): str(r["smiles"]).strip()
                   for r in csv.DictReader(f)}

    # Dumps are named by CAS, so "already generated" is a CAS-stem check, and a
    # decoy that is itself a target is excluded (targets are generated separately).
    have_dump = {p.stem for p in Path(args.fwd_dir).glob("*.pkl")}
    target_cas: set = set()
    for smi in targets.values():
        m = Chem.MolFromSmiles(smi)
        if not m:
            continue
        s = key2struct.get(Chem.MolToInchiKey(m))
        if s:
            target_cas.update(s["cas_all"])

    decoys: Dict[str, dict] = {}   # keyed by CAS
    n_targets_with_decoy = 0
    for smi in targets.values():
        m = Chem.MolFromSmiles(smi)
        if not m:
            continue
        ik = Chem.MolToInchiKey(m)
        s = key2struct.get(ik)
        if not s:
            continue
        group = [d for d in form2structs.get(s["formula"], []) if d["inchikey"] != ik]
        if group:
            n_targets_with_decoy += 1
        for d in group:
            decoys.setdefault(d["cas"], d)

    # Any registry alias having a dump means the structure is already generated -- checking
    # only d["cas"] re-queues structures that are on disk under a sibling CAS.
    need = [d for d in decoys.values()
            if not (set(d["cas_all"]) & target_cas) and not (set(d["cas_all"]) & have_dump)]
    need.sort(key=lambda d: (d["nheavy"] if d["nheavy"] is not None else 99, d["cas"]))

    def write(rows: List[dict], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["name", "smiles", "category"])
            for d in rows:
                # name = CAS (the single project-wide identifier; also the dump name).
                w.writerow([d["cas"], d["smiles"], d["formula"]])

    wave1 = [d for d in need if (d["nheavy"] or 99) <= args.max_heavy]
    wave2 = [d for d in need if (d["nheavy"] or 99) > args.max_heavy]
    write(need, out_dir / "decoys.csv")
    write(wave1, out_dir / "decoys_wave1.csv")
    write(wave2, out_dir / "decoys_wave2.csv")

    buckets = Counter()
    for d in need:
        h = d["nheavy"] or 99
        buckets["<=6" if h <= 6 else "7-9" if h <= 9 else "10-12" if h <= 12
                else "13-15" if h <= 15 else ">15"] += 1
    print(f"targets with >=1 decoy: {n_targets_with_decoy}")
    print(f"unique decoy structures: {len(decoys)} "
          f"({len(decoys)-len(need)} are a target or already dumped, {len(need)} need generation)")
    print(f"heavy-atom buckets (needed): {dict(buckets)}")
    print(f"wave 1 (<= {args.max_heavy} heavy): {len(wave1)}   wave 2: {len(wave2)}")
    print(f"wrote {out_dir/'decoys.csv'}, decoys_wave1.csv, decoys_wave2.csv")


if __name__ == "__main__":
    main()
