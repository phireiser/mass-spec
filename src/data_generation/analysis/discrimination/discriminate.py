"""Phase-1 discrimination gate — corpus runner over the NIST Parquet store.

For every target compound (``data/compounds.csv``) that has a NIST EI spectrum
*and* at least one same-formula decoy (a different structure with the same
molecular formula somewhere in the store), this measures how well the observed
spectra separate the true molecule from its isomers.

The reported baseline is the **oracle library match**: score each candidate by
``cosine(observed_true, observed_candidate)`` under the frozen unit-resolution
contract. The self-score is 1.0, so the true molecule is always rank 1; the
informative quantity is the **best-decoy cosine** -- the highest cosine any
same-formula decoy's real spectrum reaches against the query. That value is the
cosine the MØD forward model's predicted-true spectrum must exceed to identify
the molecule, so its distribution is the bar the forward half of Phase 1 must
clear.

Needs ``pyarrow`` (Parquet) and ``rdkit`` (SMILES -> InChIKey), so it runs inside
``mol-spectro.sif`` via ``run/analysis/discrimination.sh``. No ``mod`` needed --
this half of Phase 1 uses only measured spectra.

Outputs (under ``--out-dir``, default ``outputs/metrics``):
  * ``discrimination_per_target.csv``  -- one row per scored target
  * ``discrimination_summary.json``    -- corpus aggregates + run configuration
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.data_generation.analysis.discrimination import spectrum_ops as so
from src.project_paths import shared_path


# --------------------------------------------------------------------------- #
# Store loading
# --------------------------------------------------------------------------- #
def load_store(parquet_dir: Path):
    """Return ``(peaks_by_id, meta_by_id, form_to_ids)``.

    ``form_to_ids`` maps a molecular formula to the list of nist_ids of the
    *distinct structures* (deduplicated by InChIKey, first occurrence kept) that
    carry that formula in the store.
    """
    import pyarrow.parquet as pq

    idx = pq.read_table(parquet_dir / "index.parquet").to_pandas()
    spec = pq.read_table(parquet_dir / "spectra.parquet").to_pandas()

    peaks_by_id = {
        nid: [(float(x), float(y)) for x, y in zip(mz, inten)]
        for nid, mz, inten in zip(spec["nist_id"], spec["mz"], spec["intensity"])
    }
    def _str(v) -> str:
        # Parquet/pandas can hand back NaN (float) for missing text cells.
        return "" if v is None or (isinstance(v, float) and v != v) else str(v).strip()

    meta_by_id: Dict[str, Dict[str, object]] = {}
    form_to_ids: Dict[str, List[str]] = defaultdict(list)
    seen_key_per_formula: Dict[Tuple[str, str], str] = {}
    for row in idx.to_dict("records"):
        nid = row["nist_id"]
        formula = _str(row.get("formula"))
        inchikey = _str(row.get("inchikey"))
        meta_by_id[nid] = {
            "formula": formula,
            "inchikey": inchikey,
            "name": row.get("name"),
            "nominal_mw": row.get("nominal_mw"),
        }
        if formula and inchikey and nid in peaks_by_id:
            key = (formula, inchikey)
            if key not in seen_key_per_formula:  # one representative per structure
                seen_key_per_formula[key] = nid
                form_to_ids[formula].append(nid)
    return peaks_by_id, meta_by_id, dict(form_to_ids)


def resolve_inchikey(smiles: str) -> Optional[str]:
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToInchiKey(mol) if mol is not None else None


# --------------------------------------------------------------------------- #
# Per-target scoring
# --------------------------------------------------------------------------- #
def score_target(
    name: str,
    self_id: str,
    formula: str,
    peaks_by_id: Dict[str, list],
    meta_by_id: Dict[str, dict],
    decoy_ids: List[str],
) -> Dict[str, object]:
    """Library-match discrimination row for one target vs its decoys."""
    query = so.bin_spectrum(peaks_by_id[self_id])

    scored: List[Tuple[float, str]] = []
    for did in decoy_ids:
        cos = so.cosine(query, so.bin_spectrum(peaks_by_id[did]))
        scored.append((cos, did))
    scored.sort(key=lambda t: t[0], reverse=True)

    decoy_cosines = [c for c, _ in scored]
    best_cos, best_id = scored[0]
    best_meta = meta_by_id.get(best_id, {})

    # True rank among {self} u decoys: self scores 1.0, so ties (a decoy whose
    # real spectrum equals the query) are the only way the true rank slips.
    n_ties = sum(1 for c in decoy_cosines if c >= 1.0 - 1e-9)
    true_rank = 1 + n_ties

    return {
        "name": name,
        "formula": formula,
        "self_id": self_id,
        "n_decoys": len(decoy_ids),
        "best_decoy_cosine": best_cos,
        "best_decoy_name": best_meta.get("name"),
        "best_decoy_inchikey": best_meta.get("inchikey"),
        "mean_decoy_cosine": statistics.fmean(decoy_cosines),
        "median_decoy_cosine": statistics.median(decoy_cosines),
        "n_decoy_cos_gt_0.9": sum(1 for c in decoy_cosines if c > 0.9),
        "n_decoy_cos_gt_0.8": sum(1 for c in decoy_cosines if c > 0.8),
        "n_decoy_cos_gt_0.7": sum(1 for c in decoy_cosines if c > 0.7),
        "true_rank": true_rank,
        "identified": bool(true_rank == 1),
        "margin": 1.0 - best_cos,  # oracle slack: 1.0 (self) - best decoy
        "status": "ok",
    }


# --------------------------------------------------------------------------- #
# Corpus aggregates
# --------------------------------------------------------------------------- #
def _quantiles(values: List[float]) -> Dict[str, float]:
    vals = sorted(values)
    if not vals:
        return {}

    def q(p: float) -> float:
        if len(vals) == 1:
            return vals[0]
        i = p * (len(vals) - 1)
        lo = int(i)
        frac = i - lo
        hi = min(lo + 1, len(vals) - 1)
        return vals[lo] * (1 - frac) + vals[hi] * frac

    return {"p10": q(0.10), "p25": q(0.25), "p50": q(0.50), "p75": q(0.75), "p90": q(0.90)}


def all_pair_cross_isomer(peaks_by_id, form_to_ids, max_group: int) -> Dict[str, object]:
    """Cross-isomer cosine over *every* same-formula pair in the store (a broad
    premise read, independent of the target set). Groups larger than
    ``max_group`` structures are skipped to bound the O(n^2) cost."""
    cosines: List[float] = []
    n_groups = 0
    for formula, ids in form_to_ids.items():
        if len(ids) < 2 or len(ids) > max_group:
            continue
        n_groups += 1
        vecs = [so.bin_spectrum(peaks_by_id[i]) for i in ids]
        for a in range(len(vecs)):
            for b in range(a + 1, len(vecs)):
                cosines.append(so.cosine(vecs[a], vecs[b]))
    if not cosines:
        return {"n_pairs": 0, "n_groups": 0}
    return {
        "n_pairs": len(cosines),
        "n_groups": n_groups,
        "mean": statistics.fmean(cosines),
        "median": statistics.median(cosines),
        "quantiles": _quantiles(cosines),
        "frac_gt_0.9": sum(1 for c in cosines if c > 0.9) / len(cosines),
        "frac_gt_0.7": sum(1 for c in cosines if c > 0.7) / len(cosines),
    }


def summarize(rows: List[Dict[str, object]], cross_isomer: Dict[str, object],
              config: Dict[str, object]) -> Dict[str, object]:
    ok = [r for r in rows if r.get("status") == "ok"]
    best = [float(r["best_decoy_cosine"]) for r in ok]
    margins = [float(r["margin"]) for r in ok]
    n_ident = sum(1 for r in ok if r["identified"])
    return {
        "config": config,
        "n_targets_scored": len(ok),
        "n_targets_skipped": len(rows) - len(ok),
        "oracle_top1_accuracy": (n_ident / len(ok)) if ok else float("nan"),
        "best_decoy_cosine": {
            "mean": statistics.fmean(best) if best else float("nan"),
            "median": statistics.median(best) if best else float("nan"),
            "quantiles": _quantiles(best),
            "n_targets_with_hard_decoy_gt_0.9": sum(1 for c in best if c > 0.9),
            "n_targets_with_decoy_gt_0.7": sum(1 for c in best if c > 0.7),
        },
        "margin": {
            "mean": statistics.fmean(margins) if margins else float("nan"),
            "median": statistics.median(margins) if margins else float("nan"),
            "quantiles": _quantiles(margins),
        },
        "cross_isomer_all_pairs": cross_isomer,
        "hardest_targets": [
            {"name": r["name"], "formula": r["formula"],
             "best_decoy_cosine": r["best_decoy_cosine"],
             "best_decoy_name": r["best_decoy_name"], "n_decoys": r["n_decoys"]}
            for r in sorted(ok, key=lambda r: -float(r["best_decoy_cosine"]))[:15]
        ],
        "skipped": [
            {"name": r["name"], "status": r["status"]}
            for r in rows if r.get("status") != "ok"
        ],
    }


def write_csv(rows: List[Dict[str, object]], path: Path) -> None:
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
    parser = argparse.ArgumentParser(
        description="Phase-1 true-vs-same-formula-decoy discrimination gate")
    parser.add_argument("--spectra-folder", type=str,
                        default=str(shared_path("PARQUET_DIR_REL")),
                        help="NIST spectra Parquet store")
    parser.add_argument("--compounds-csv", type=str,
                        default=str(shared_path("CSV_PATH_REL")),
                        help="CSV mapping molecule name -> SMILES (the target set)")
    parser.add_argument("--out-dir", type=str,
                        default=str(shared_path("METRICS_DIR_REL")),
                        help="Directory for discrimination outputs")
    parser.add_argument("--names", type=str, default="",
                        help="Comma-separated subset of target names (default: all)")
    parser.add_argument("--max-group", type=int, default=80,
                        help="Skip formula groups larger than this in the all-pairs scan")
    args = parser.parse_args()

    parquet_dir = Path(args.spectra_folder)
    out_dir = Path(args.out_dir)

    with open(args.compounds_csv, newline="", encoding="utf-8") as f:
        name2smiles = {str(r["name"]).strip(): str(r["smiles"]).strip()
                       for r in csv.DictReader(f)}
    only = {n.strip() for n in args.names.split(",") if n.strip()} if args.names else None

    peaks_by_id, meta_by_id, form_to_ids = load_store(parquet_dir)
    key_to_id = {meta["inchikey"]: nid for nid, meta in meta_by_id.items()
                 if meta.get("inchikey") and nid in peaks_by_id}
    print(f"Store: {len(peaks_by_id)} spectra, {len(form_to_ids)} formulas with a spectrum")

    rows: List[Dict[str, object]] = []
    for name, smiles in sorted(name2smiles.items()):
        if only and name not in only:
            continue
        ikey = resolve_inchikey(smiles)
        if ikey is None:
            rows.append({"name": name, "status": "error: unparseable SMILES"})
            continue
        self_id = key_to_id.get(ikey)
        if self_id is None:
            rows.append({"name": name, "status": "skip: no spectrum in store"})
            continue
        formula = meta_by_id[self_id]["formula"]
        decoy_ids = [nid for nid in form_to_ids.get(formula, [])
                     if meta_by_id[nid]["inchikey"] != ikey]
        if not decoy_ids:
            rows.append({"name": name, "formula": formula, "n_decoys": 0,
                         "status": "skip: no same-formula decoy"})
            continue
        row = score_target(name, self_id, formula, peaks_by_id, meta_by_id, decoy_ids)
        rows.append(row)
        print(f"  {name:24s} {formula:12s} decoys={row['n_decoys']:3d}  "
              f"best_decoy_cos={row['best_decoy_cosine']:.3f}  "
              f"(nearest: {row['best_decoy_name']})")

    cross = all_pair_cross_isomer(peaks_by_id, form_to_ids, args.max_group)
    config = {
        "binning": "nominal (floor) m/z, sqrt-intensity, L2, dot-product cosine",
        "mz_min": so.MZ_MIN, "mz_max": so.MZ_MAX, "bin_width": so.BIN_WIDTH,
        "ion_mode": "EI M+•", "max_group": args.max_group,
    }
    summary = summarize(rows, cross, config)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(rows, out_dir / "discrimination_per_target.csv")
    with open(out_dir / "discrimination_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    b = summary["best_decoy_cosine"]
    print(f"\nScored {summary['n_targets_scored']} targets with >=1 same-formula decoy.")
    print(f"Oracle library-match top-1 accuracy: {summary['oracle_top1_accuracy']:.3f}")
    print(f"Best-decoy cosine (the bar the forward model must beat): "
          f"mean={b['mean']:.3f} median={b['median']:.3f}; "
          f"{b['n_targets_with_hard_decoy_gt_0.9']} targets have a decoy > 0.9")
    if cross.get("n_pairs"):
        print(f"All same-formula pairs (n={cross['n_pairs']}): "
              f"median cross-isomer cosine {cross['median']:.3f}, "
              f"{cross['frac_gt_0.9']*100:.1f}% > 0.9")
    print(f"Wrote {out_dir/'discrimination_per_target.csv'} and "
          f"{out_dir/'discrimination_summary.json'}")


if __name__ == "__main__":
    main()
