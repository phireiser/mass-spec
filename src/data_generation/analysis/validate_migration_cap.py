#!/usr/bin/env python3
"""Is the multiplicity cap lossless on the molecules the ring clause newly captures?

``strategy.migration_scope``'s cap was measured lossless on exactly two molecules, both
steroids (progesterone, cholesterol). The ``min_cyclomatic`` clause extends the cap to
saturated polycyclic terpenoids -- structurally the same fused-saturated-cage motif, but an
extrapolation nonetheless, and the only real risk in that change. So measure it.

The control is free: the uncapped dumps already exist in ``data/processed/fwd`` from the decoy
build (job 5824027) and the corpus build. This compares them against a capped rebuild
(``PROCESSED_DIR_OVERRIDE=data/processed_capval``) and reports what the cap actually costs.

**Mass sets, not TPR.** TPR/Dice saturate on large molecules -- a steroid's NIST reference
covers ~75 % of the candidate integer masses, so a random emitter scores well (progesterone
hit 0.810 vs 0.793 by chance, p=0.56). Every molecule here is large, so the verdict is a set
difference on nominal m/z. The headline is how many *NIST-observed* masses the cap drops:
losing a mass the instrument never recorded costs nothing.

Reads species through :func:`utils.get_spectra_from_dump`, so it never loads a DG and never
touches mod's process-global graph database -- the whole 83-molecule sweep runs in one
process in minutes.

    # build the capped arm first:
    PROCESSED_DIR_OVERRIDE=data/processed_capval DEFINITION_FILE=data/cap_validation.csv \
        sbatch run/hpc/data_gen.sh
    # then:
    python src/data_generation/analysis/validate_migration_cap.py

**Result: the extrapolation FAILED.** Cap 2 loses at least one NIST-observed mass on 38 of the
83, cap 3 on 33 (2.4x the cost for 5 molecules), so the loss is structural, not a threshold
artifact. Cap 2 ships anyway on the *size* of the loss -- max 0.98% of occurrence weight, zero
molecules above 1% -- and because 8 of these 83 exceeded the old 12h30/8GB budget, where the
alternative is no dump at all. Details and the full table live in ``strategy.migration_scope``.
Re-run with ``--capped-dir data/processed_capval3/fwd`` to reproduce the cap-3 arm.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

from src.data_generation import utils
from src.project_paths import shared_path


def mass_profile(stem: str, fwd_dir: Path):
    """(nominal-m/z set, per-mass occurrence weights) for a dump, or (None, None)."""
    if not stem or not utils.dump_is_complete(stem, path=fwd_dir):
        return None, None
    try:
        spectra = utils.get_spectra_from_dump(stem, path=fwd_dir)
    except Exception:  # noqa: BLE001 - a truncated dump must not kill the sweep
        return None, None
    if not spectra:
        return None, None
    weights = {}
    for mass, occurrence, _rules in spectra:
        m = int(round(float(mass)))
        weights[m] = weights.get(m, 0.0) + float(occurrence)
    return set(weights), weights


def nist_masses(smiles: str, parquet: Path):
    """Nominal masses NIST actually observes, or None if the molecule is not in the store."""
    try:
        peaks = utils.get_spectra_by_smiles(smiles, parquet)
    except Exception:  # noqa: BLE001 - a store miss is not a failure
        return None
    if not peaks:
        return None
    try:
        return {int(round(float(p[0]))) for p in peaks}
    except Exception:  # noqa: BLE001 - unexpected shape
        return None


def compare(name: str, smiles: str, uncapped_dir: Path, capped_dir: Path, parquet: Path):
    cas = utils.get_cas_by_smiles(smiles, parquet) or name
    unc, unc_w = mass_profile(cas, uncapped_dir)
    cap, _ = mass_profile(cas, capped_dir)
    row = {"name": name, "cas": cas, "smiles": smiles}
    if unc is None or cap is None:
        row["status"] = (f"missing arm (uncapped={unc is not None}, "
                         f"capped={cap is not None})")
        return row
    lost, gained = unc - cap, cap - unc
    row.update({
        "status": "ok",
        "n_uncapped": len(unc), "n_capped": len(cap),
        "n_lost": len(lost), "n_gained": len(gained),
        "lost": sorted(lost)[:40],
        # what the lost masses were worth, by the forward model's own occurrence weights
        "lost_occurrence_share": round(
            sum(unc_w[m] for m in lost) / sum(unc_w.values()), 5) if unc_w else None,
    })
    observed = nist_masses(smiles, parquet)
    if observed is not None:
        row["n_nist"] = len(observed)
        row["n_lost_and_observed"] = len(lost & observed)
        row["lost_and_observed"] = sorted(lost & observed)[:40]
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--definition", default="data/cap_validation.csv",
                    help="name,smiles,category CSV of the molecules to check")
    ap.add_argument("--uncapped-dir", default=str(shared_path("PROCESSED_DIR_REL", "fwd")))
    ap.add_argument("--capped-dir", default="data/processed_capval/fwd")
    ap.add_argument("--spectra-folder", default=str(shared_path("PARQUET_DIR_REL")))
    ap.add_argument("--out", default="data/outputs/metrics/cap_validation.json")
    args = ap.parse_args()

    uncapped, capped = Path(args.uncapped_dir), Path(args.capped_dir)
    parquet = Path(args.spectra_folder)
    with open(args.definition, newline="", encoding="utf-8") as fh:
        molecules = [(r["name"].strip(), r["smiles"].strip()) for r in csv.DictReader(fh)]

    rows = []
    for i, (name, smiles) in enumerate(molecules, 1):
        row = compare(name, smiles, uncapped, capped, parquet)
        rows.append(row)
        print(f"  [{i}/{len(molecules)}] {name[:38]:38s} {row['status']}"
              + (f"  lost {row['n_lost']}/{row['n_uncapped']}"
                 f"  NIST-observed lost {row.get('n_lost_and_observed', '?')}"
                 if row["status"] == "ok" else ""), flush=True)

    ok = [r for r in rows if r["status"] == "ok"]
    lossless = [r for r in ok if r["n_lost"] == 0]
    safe = [r for r in ok if r.get("n_lost_and_observed", 0) == 0]
    gained = [r for r in ok if r["n_gained"] > 0]
    verdict = bool(ok) and len(safe) == len(ok) and not gained

    summary = {
        "n_molecules": len(rows), "n_compared": len(ok),
        "n_mass_set_lossless": len(lossless),
        "n_lost_no_observed_mass": len(safe),
        "n_gained_masses": len(gained),
        "verdict": "PASS" if verdict else "FAIL",
        "per_molecule": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1))

    print(f"\ncompared {len(ok)}/{len(rows)} molecules (both arms present)")
    print(f"  mass-set lossless (n_lost == 0)   : {len(lossless)}/{len(ok)}")
    print(f"  lost NO NIST-observed mass        : {len(safe)}/{len(ok)}")
    print(f"  gained masses (must be 0)         : {len(gained)}")
    worst = sorted(ok, key=lambda r: -r.get("n_lost_and_observed", 0))[:8]
    if worst:
        print("  worst by NIST-observed masses lost:")
        for r in worst:
            print(f"    {r['name'][:36]:36s} lost {r['n_lost']:4d}/{r['n_uncapped']:4d}"
                  f"  observed-lost {r.get('n_lost_and_observed', '?'):>3}"
                  f"  occ-share {r.get('lost_occurrence_share')}")
    print(f"\n  VERDICT: {summary['verdict']}"
          f"{' -- cap costs no NIST-observed mass' if verdict else ' -- inspect above'}")
    print(f"  wrote {out}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
