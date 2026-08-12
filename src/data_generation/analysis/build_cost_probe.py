#!/usr/bin/env python3
"""Stage-0 sampler: a heavy-atom-stratified probe set for the build-cost model.

The selective-teacher gate (``docs/PHASE2_PLAN.md``) turns on ``N* ~ B / cost_per_molecule``,
and every cost figure the project has so far comes from two samples that are both biased small
-- the 172-molecule curated corpus and the 1155 same-formula decoys, none above ~28 heavy
atoms. The store runs to 69. Extrapolating full-enumeration cost from those would understate
the tail badly, which is the exact quantity the gate depends on.

**Stratified with equal n per bin, not proportional.** A proportional sample of the store puts
~75% of its draws below 16 heavy atoms, where cost is small and already well characterised, and
almost nothing in the tail where the variance lives. Equal-n bins buy precision where it
matters; the store's real bin frequencies are carried in the manifest so the extrapolation
reweights back to the true distribution:

    total_cost ~ SUM_bin  store_count[bin] * mean_cost[bin]

Molecules that already have a dump are excluded -- ``--avoid-reprocessing`` would skip them and
they would contribute no timing.

Writes ``data/cost_probe.csv`` (the main arm) plus ``data/cost_probe_small.csv``, a subset used
for the rule-count and guard-state sensitivity arms, which are rebuilt several times each and
so must stay cheap. Manifest goes to ``data/outputs/metrics/cost_probe_manifest.json``.

Needs pyarrow + rdkit, so run inside the container.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

from src.project_paths import shared_path

# (label, lo, hi) inclusive heavy-atom bins. Boundaries follow the store's own quantiles
# (p25=9, p50=12, p75=16, p90=21, p95=26, p99=34, max=69) so no bin is nearly empty.
BINS = [
    ("00-06", 0, 6), ("07-09", 7, 9), ("10-12", 10, 12), ("13-15", 13, 15),
    ("16-18", 16, 18), ("19-21", 19, 21), ("22-26", 22, 26), ("27-34", 27, 34),
    ("35-69", 35, 999),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spectra-folder", default=str(shared_path("PARQUET_DIR_REL")))
    ap.add_argument("--fwd-dir", default=str(shared_path("PROCESSED_DIR_REL", "fwd")))
    ap.add_argument("--out-dir", default=str(shared_path("DATA_DIR_REL")))
    ap.add_argument("--metrics-dir", default=str(shared_path("METRICS_DIR_REL")))
    ap.add_argument("--per-bin", type=int, default=22, help="molecules sampled per bin")
    ap.add_argument("--per-bin-small", type=int, default=4,
                    help="per bin for the sensitivity subset (rebuilt many times)")
    ap.add_argument("--seed", type=int, default=20260812)
    args = ap.parse_args()

    import pyarrow.parquet as pq
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")

    pqdir = Path(args.spectra_folder)
    idx = pq.read_table(pqdir / "index.parquet").to_pandas()
    spec_ids = set(pq.read_table(pqdir / "spectra.parquet").to_pandas()["nist_id"])
    have_dump = {p.stem for p in Path(args.fwd_dir).glob("*.done")}

    by_bin: dict = {b[0]: [] for b in BINS}
    store_counts: dict = {b[0]: 0 for b in BINS}
    seen_key: set = set()

    for r in idx.to_dict("records"):
        if r["nist_id"] not in spec_ids:
            continue
        smiles = r.get("canonical_smiles") or r.get("isomeric_smiles")
        cas = str(r.get("cas") or "").strip()
        if not smiles or not isinstance(smiles, str):
            continue
        mol = Chem.MolFromSmiles(smiles)
        if mol is None or mol.GetNumHeavyAtoms() < 1:
            continue
        if any(a.GetIsotope() for a in mol.GetAtoms()):
            continue
        key = Chem.MolToInchiKey(mol)
        if key in seen_key:
            continue
        seen_key.add(key)

        n = mol.GetNumHeavyAtoms()
        label = next((b[0] for b in BINS if b[1] <= n <= b[2]), None)
        if label is None:
            continue
        store_counts[label] += 1
        # Eligible for sampling only if it is not already built (a skipped task times nothing)
        # and it has a CAS, so the dump name matches how every other build is keyed.
        if cas and cas not in have_dump:
            by_bin[label].append({"cas": cas, "smiles": Chem.MolToSmiles(mol),
                                  "nheavy": n, "inchikey": key})

    rng = random.Random(args.seed)
    main_rows, small_rows, manifest = [], [], []
    for label, lo, hi in BINS:
        pool = by_bin[label]
        rng.shuffle(pool)
        take = pool[:args.per_bin]
        main_rows += take
        small_rows += take[:args.per_bin_small]
        manifest.append({
            "bin": label, "lo": lo, "hi": hi,
            "store_count": store_counts[label],      # reweighting factor for extrapolation
            "eligible": len(pool), "sampled": len(take),
            "sampled_small": len(take[:args.per_bin_small]),
        })
        print(f"  {label}: store {store_counts[label]:6d}  eligible {len(pool):6d}  "
              f"sampled {len(take):3d}")

    out_dir = Path(args.out_dir)

    def write(rows, path: Path) -> None:
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["name", "smiles", "category"])
            for r in rows:
                # name = CAS, matching how every dump in the project is keyed.
                w.writerow([r["cas"], r["smiles"], f"cost_probe_{r['nheavy']}heavy"])
        print(f"wrote {path} ({len(rows)} molecules)")

    write(main_rows, out_dir / "cost_probe.csv")
    write(small_rows, out_dir / "cost_probe_small.csv")

    mpath = Path(args.metrics_dir) / "cost_probe_manifest.json"
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps({
        "seed": args.seed, "per_bin": args.per_bin, "per_bin_small": args.per_bin_small,
        "store_total": sum(store_counts.values()),
        "bins": manifest,
        "molecules": {r["cas"]: {"nheavy": r["nheavy"], "smiles": r["smiles"]}
                      for r in main_rows},
    }, indent=1))
    print(f"wrote {mpath}")
    print(f"store total (deduped, with spectrum): {sum(store_counts.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
