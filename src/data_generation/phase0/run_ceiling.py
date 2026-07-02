"""
Phase 0.1 corpus runner — the MØD explainability ceiling.

For every molecule that has *both* a forward derivation-graph dump (under
``data/processed/fwd/``) and a NIST EI spectrum (in the Parquet store, looked up
by SMILES), this computes how much of the experimental peak intensity the MØD rule library can
explain, with a random-formula null subtracted, plus the M+• presence and the
odd/even-electron split of the unexplained peaks.

This is the only Phase-0 module that needs ``mod``; it loads each dump, pulls the
charged-fragment nominal masses, and defers every numeric decision to the pure
functions in :mod:`ceiling_metrics`. Run it inside ``mol-spectro.sif`` via
``run/analysis/phase0_ceiling.sh``.

Outputs (under ``--out-dir``, default ``outputs/phase0``):
  * ``ceiling_per_molecule.csv`` — one row per analyzed molecule
  * ``ceiling_summary.json``     — corpus aggregates + the run configuration
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import traceback
from pathlib import Path
from typing import Dict, List, Optional

from src.data_generation import utils
from src.data_generation.phase0 import ceiling_metrics as cm
from src.project_paths import shared_path


def _finite(values) -> List[float]:
    return [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]


def _mean(values) -> float:
    vals = _finite(values)
    return statistics.fmean(vals) if vals else float("nan")


def _mod_masses(name: str, fwd_dir: Path) -> set:
    """Nominal (round) masses of the charged MØD fragments in a forward dump."""
    dg = utils.load_derivation_graph(name, path=fwd_dir)
    spectra = utils.get_spectra_from_mod_derivation_graph(dg)
    return {round(mass) for mass, _occ, _rules in spectra}


def analyze_molecule(
    name: str,
    smiles: str,
    fwd_dir: Path,
    parquet_dir: Path,
    *,
    taus: List[float],
    primary_tau: float,
    draws: int,
    extra_h: int,
    rng: random.Random,
) -> Dict[str, object]:
    """Compute the full ceiling metric row for one molecule.

    Raises on unrecoverable problems (missing spectrum, unreadable dump); the
    caller records those as skipped. A missing/garbled formula degrades
    gracefully: the null and OE/EE columns are left as ``nan`` while the raw
    explained fractions are still reported.
    """
    record = utils.get_record_by_smiles(smiles, parquet_dir)
    if not record:
        raise FileNotFoundError(f"no spectrum in Parquet store for {name} ({smiles})")
    peaks = record["peaks"]
    mod_masses = _mod_masses(name, fwd_dir)

    formula = record.get("formula") or ""
    inventory = cm.parse_formula(formula) if formula else {}
    n_nitrogen = cm.nitrogen_count(inventory)

    # M+• nominal mass: prefer the stored nominal MW, else the heaviest fragment.
    mplus: Optional[int] = int(record["nominal_mw"]) if record.get("nominal_mw") else None
    if mplus is None and mod_masses:
        mplus = max(mod_masses)

    row: Dict[str, object] = {
        "name": name,
        "formula": formula,
        "n_nitrogen": n_nitrogen,
        "mplus_nominal": mplus if mplus is not None else "",
        "n_peaks_total": len(peaks),
        "n_mod_masses": len(mod_masses),
    }

    # Raw explained fraction across the threshold sweep (intensity-weighted),
    # always restricted to peaks at or below the molecular ion.
    base = max((inten for _, inten in peaks), default=0.0)
    for tau in taus:
        sel = cm.select_peaks(peaks, intensity_floor=tau * base, mz_max=mplus)
        row[f"raw_int_tau{tau:g}"] = cm.explained_fraction(sel, mod_masses, weighted=True)
        row[f"raw_cnt_tau{tau:g}"] = cm.explained_fraction(sel, mod_masses, weighted=False)

    # Primary high-intensity set drives the null-subtracted ceiling.
    sel = cm.select_peaks(peaks, intensity_floor=primary_tau * base, mz_max=mplus)
    raw_hi = cm.explained_fraction(sel, mod_masses, weighted=True)
    row["raw_int_hi"] = raw_hi
    row["n_peaks_scored_hi"] = len(sel)

    # Null models (need a formula for the formula-aware pool and a mass ceiling).
    null_formula = float("nan")
    null_uniform = float("nan")
    ceiling = float("nan")
    ci_lo = ci_hi = float("nan")
    unsupported = sorted(e for e in inventory if e not in cm.NOMINAL_MASS)
    if mplus and inventory and not unsupported and len(mod_masses) > 0:
        pool = cm.formula_reachable_masses(inventory, mplus, extra_h=extra_h)
        null_formula, _ci_f, fr_formula = cm.sample_null(
            pool, len(mod_masses), sel, draws=draws, weighted=True, rng=rng
        )
        null_uniform, _ci_u, _fr_u = cm.sample_null(
            cm.uniform_pool(mplus), len(mod_masses), sel, draws=draws, weighted=True, rng=rng
        )
        ceiling, (ci_lo, ci_hi) = cm.ceiling_with_ci(raw_hi, fr_formula)

    row["null_formula"] = null_formula
    row["null_uniform"] = null_uniform
    row["ceiling"] = ceiling
    row["ceiling_ci_lo"] = ci_lo
    row["ceiling_ci_hi"] = ci_hi
    row["unsupported_elements"] = ",".join(unsupported)

    # M+• presence: in the spectrum and produced by MØD.
    spectrum_nominal = {round(mz) for mz, inten in peaks if inten > 0}
    row["mplus_in_spectrum"] = bool(mplus in spectrum_nominal) if mplus else ""
    row["mplus_in_mod"] = bool(mplus in mod_masses) if mplus else ""

    # Odd/even-electron split of the *unexplained* high-intensity intensity.
    unexplained = [(mz, inten) for mz, inten in sel if round(mz) not in mod_masses]
    oe = math.fsum(inten for mz, inten in unexplained
                   if cm.nitrogen_rule_parity(round(mz), n_nitrogen) == "OE")
    ee = math.fsum(inten for mz, inten in unexplained
                   if cm.nitrogen_rule_parity(round(mz), n_nitrogen) == "EE")
    tot = oe + ee
    row["unexpl_OE_frac"] = oe / tot if tot > 0 else float("nan")
    row["unexpl_EE_frac"] = ee / tot if tot > 0 else float("nan")
    row["unexpl_intensity_frac"] = tot / math.fsum(i for _, i in sel) if sel else float("nan")
    row["status"] = "ok"
    return row


def discover_names(fwd_dir: Path, name2smiles: Dict[str, str], parquet_dir: Path,
                   only: Optional[List[str]]) -> List[str]:
    """Names with both a dump (``.pkl``) and a spectrum in the Parquet store,
    sorted; ``only`` filters."""
    have_dump = {p.stem for p in fwd_dir.glob("*.pkl")}
    if only:
        wanted = [n.strip() for n in only if n.strip()]
        names = [n for n in wanted if n in have_dump]
    else:
        names = sorted(have_dump)
    return [n for n in names
            if n in name2smiles and utils.get_spectra_by_smiles(name2smiles[n], parquet_dir)]


def summarize(rows: List[Dict[str, object]], config: Dict[str, object]) -> Dict[str, object]:
    ok = [r for r in rows if r.get("status") == "ok"]
    taus = config["taus"]

    def rate(key: str) -> float:
        vals = [r[key] for r in ok if isinstance(r.get(key), bool)]
        return (sum(1 for v in vals if v) / len(vals)) if vals else float("nan")

    ceilings = _finite([r["ceiling"] for r in ok])
    summary = {
        "config": config,
        "n_with_dump_and_spectrum": len(rows),
        "n_ok": len(ok),
        "n_skipped": len(rows) - len(ok),
        "ceiling": {
            "mean": _mean(ceilings),
            "median": statistics.median(ceilings) if ceilings else float("nan"),
            "min": min(ceilings) if ceilings else float("nan"),
            "max": max(ceilings) if ceilings else float("nan"),
            "n": len(ceilings),
        },
        "raw_int_hi_mean": _mean([r.get("raw_int_hi") for r in ok]),
        "null_formula_mean": _mean([r.get("null_formula") for r in ok]),
        "null_uniform_mean": _mean([r.get("null_uniform") for r in ok]),
        "mplus_in_spectrum_rate": rate("mplus_in_spectrum"),
        "mplus_in_mod_rate": rate("mplus_in_mod"),
        "unexpl_OE_frac_mean": _mean([r.get("unexpl_OE_frac") for r in ok]),
        "unexpl_EE_frac_mean": _mean([r.get("unexpl_EE_frac") for r in ok]),
        "tau_sweep_raw_int_mean": {
            f"{tau:g}": _mean([r.get(f"raw_int_tau{tau:g}") for r in ok]) for tau in taus
        },
        "skipped": [
            {"name": r["name"], "status": r["status"]} for r in rows if r.get("status") != "ok"
        ],
        "unsupported_element_molecules": [
            {"name": r["name"], "elements": r["unsupported_elements"]}
            for r in ok if r.get("unsupported_elements")
        ],
    }
    return summary


def write_csv(rows: List[Dict[str, object]], path: Path) -> None:
    # Union of keys preserves order of first appearance across rows.
    fields: List[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 0.1 MØD explainability ceiling")
    parser.add_argument("--fwd-dir", type=str, default=str(shared_path("PROCESSED_DIR_REL", "fwd")),
                        help="Directory of forward DG dumps (.dmp/.pkl)")
    parser.add_argument("--spectra-folder", type=str, default=str(shared_path("PARQUET_DIR_REL")),
                        help="Directory of the NIST spectra Parquet store")
    parser.add_argument("--compounds-csv", type=str, default=str(shared_path("CSV_PATH_REL")),
                        help="CSV mapping molecule name -> SMILES (for parquet lookup)")
    parser.add_argument("--out-dir", type=str, default=str(shared_path("PHASE0_DIR_REL")),
                        help="Directory for ceiling outputs")
    parser.add_argument("--names", type=str, default="",
                        help="Comma-separated subset of molecule names (default: all)")
    parser.add_argument("--draws", type=int, default=1000, help="Null sampling draws")
    parser.add_argument("--primary-tau", type=float, default=0.01,
                        help="High-intensity threshold (fraction of base peak) for the ceiling")
    parser.add_argument("--taus", type=str, default="0,0.01,0.05,0.10",
                        help="Comma-separated threshold sweep for the raw explained fraction")
    parser.add_argument("--extra-h", type=int, default=2,
                        help="Hydrogen slack above precursor-H for the formula-aware null")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed for null sampling")
    args = parser.parse_args()

    fwd_dir = Path(args.fwd_dir)
    parquet_dir = Path(args.spectra_folder)
    out_dir = Path(args.out_dir)
    taus = [float(t) for t in args.taus.split(",") if t.strip() != ""]
    rng = random.Random(args.seed)

    with open(args.compounds_csv, newline="", encoding="utf-8") as f:
        name2smiles = {str(r["name"]).strip(): str(r["smiles"]).strip()
                       for r in csv.DictReader(f)}

    only = args.names.split(",") if args.names else None
    names = discover_names(fwd_dir, name2smiles, parquet_dir, only)
    print(f"Phase 0.1: {len(names)} molecules with both a dump and a spectrum")

    rows: List[Dict[str, object]] = []
    for i, name in enumerate(names, 1):
        try:
            row = analyze_molecule(
                name, name2smiles[name], fwd_dir, parquet_dir,
                taus=taus, primary_tau=args.primary_tau,
                draws=args.draws, extra_h=args.extra_h, rng=rng,
            )
            print(f"  [{i}/{len(names)}] {name}: ceiling={row['ceiling']!s:.6}  "
                  f"raw={row['raw_int_hi']!s:.6}  null={row['null_formula']!s:.6}")
        except Exception as exc:  # noqa: BLE001 - one bad dump must not kill the run
            row = {"name": name, "status": f"error: {exc}"}
            print(f"  [{i}/{len(names)}] {name}: SKIPPED ({exc})")
            traceback.print_exc()
        rows.append(row)

    config = {
        "primary_tau": args.primary_tau, "taus": taus, "draws": args.draws,
        "extra_h": args.extra_h, "seed": args.seed,
        "binning": "nominal (round) m/z", "ion_mode": "EI M+•",
    }
    summary = summarize(rows, config)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(rows, out_dir / "ceiling_per_molecule.csv")
    with open(out_dir / "ceiling_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    c = summary["ceiling"]
    print(f"\nPhase 0.1 ceiling: mean={c['mean']:.3f} median={c['median']:.3f} "
          f"(n={c['n']}); M+• in spectrum {summary['mplus_in_spectrum_rate']:.2f}, "
          f"in MØD {summary['mplus_in_mod_rate']:.2f}")
    print(f"Wrote {out_dir/'ceiling_per_molecule.csv'} and {out_dir/'ceiling_summary.json'}")


if __name__ == "__main__":
    main()
