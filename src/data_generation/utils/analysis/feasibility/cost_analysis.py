"""
Per-molecule MØD cost and the full-enumeration budget crossover (feasibility study).

The ceiling analysis asks whether the rule library *can* explain the spectra; this
asks whether enumerating the full forward derivation graph for every molecule is
*affordable*, and if not, past what corpus size selective/RL construction has to
take over (see the de-risked plan: ``N* = B / cost_per_molecule``).

Cost unit is **wall-clock seconds** taken from ``sacct`` (the ``time -v`` numbers in
the logs measure the ``srun`` launcher, not the container payload, so they are
useless for RSS/CPU — only their elapsed field is real, and sacct is cleaner). The
per-round "Result subset has N graphs" counts are parsed too, but only as a
diagnostic: they do *not* predict cost — saturated aliphatics finish with a tiny
output DG yet dominate the runtime in the ``sub_group`` rightPredicate. So the graph
count is reported, never used as the budget driver.

Tasks that hit the SLURM wall (TIMEOUT) are **right-censored**: their true cost is
only known to be ``>= elapsed``. Any mean over the finishers is therefore a lower
bound on the real per-molecule cost, and the reported N* is an *upper* bound on the
affordable corpus. OOM (FAILED) and NODE_FAIL tasks carry no usable cost and are
tallied separately.

This module is stdlib-only (no ``mod``/numpy) so it runs bare on the login node,
straight over the sacct dump + the array logs. Inputs:
  * ``--sacct-file``  pipe-delimited ``sacct -j <id> -P`` dump with fields
                      ``JobID|State|ElapsedRaw|MaxRSS|ReqMem`` (main step + ``.batch``
                      + ``.0`` substeps), or ``--job-id`` to shell out to sacct.
  * ``--manifest``    the ``name<TAB>smiles`` manifest the array indexed into.
  * ``--log-dir``     the ``<jobid>/`` dir of ``<idx>__<name>.out`` task logs.
Outputs (under ``--out-dir``):
  * ``cost_per_molecule.csv`` — one row per array task
  * ``cost_summary.json``     — finisher stats, censoring tally, N* table
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Budgets to tabulate N* against, in core-hours (1 core/task, so core-h == wall-h).
DEFAULT_BUDGETS_CORE_H = [100, 500, 1000, 5000, 10000]

_GRAPHS_RE = re.compile(r"Result subset has (\d+) graphs")


def parse_sacct(text: str) -> Dict[int, Dict[str, object]]:
    """Fold a pipe-delimited sacct dump into one record per array task index.

    The main step (``<job>_<idx>``) carries State/ElapsedRaw/ReqMem; MaxRSS lives on
    the ``.0`` substep. We merge them onto the array index.
    """
    rows: Dict[int, Dict[str, object]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) < 5:
            continue
        job_id, state, elapsed_raw, max_rss, req_mem = parts[:5]
        m = re.match(r".*_(\d+)(?:\.(\S+))?$", job_id)
        if not m:
            continue
        idx = int(m.group(1))
        step = m.group(2)  # None for main step, "batch"/"0" for substeps
        rec = rows.setdefault(idx, {"idx": idx})
        if step is None:
            rec["state"] = state
            rec["elapsed_s"] = int(elapsed_raw) if elapsed_raw.isdigit() else None
            rec["req_mem"] = req_mem
        elif step == "0":
            rec["max_rss_kb"] = _parse_rss_kb(max_rss)
    return rows


def _parse_rss_kb(raw: str) -> Optional[int]:
    """sacct MaxRSS like '289600K' / '1.02G' / '' -> kilobytes."""
    raw = raw.strip()
    if not raw:
        return None
    unit = raw[-1]
    try:
        val = float(raw[:-1]) if unit.isalpha() else float(raw)
    except ValueError:
        return None
    scale = {"K": 1, "M": 1024, "G": 1024 * 1024, "T": 1024 * 1024 * 1024}
    return int(val * scale.get(unit, 1))


def parse_manifest(path: Path) -> Dict[int, str]:
    """1-based line index -> molecule name (matches the SLURM array indexing)."""
    names: Dict[int, str] = {}
    for i, line in enumerate(path.read_text().splitlines(), start=1):
        line = line.rstrip("\r")
        if not line:
            continue
        names[i] = line.split("\t", 1)[0]
    return names


def parse_log_graphs(log_dir: Path, idx: int, name: str) -> Tuple[Optional[int], Optional[int]]:
    """Return (sum_graphs, max_round_graphs) from the task log, or (None, None).

    Diagnostic only — not a cost predictor (see module docstring).
    """
    matches = list(log_dir.glob(f"{idx}__{name}.out"))
    if not matches:
        matches = list(log_dir.glob(f"{idx}__*.out"))
    if not matches:
        return None, None
    counts = [int(x) for x in _GRAPHS_RE.findall(matches[0].read_text(errors="replace"))]
    if not counts:
        return None, None
    return sum(counts), max(counts)


def classify(state: str) -> str:
    """Map a raw sacct state to a cost bucket."""
    if state == "COMPLETED":
        return "finished"
    if state == "TIMEOUT":
        return "censored_timeout"  # true cost >= elapsed
    if state in ("FAILED", "OUT_OF_MEMORY"):
        return "oom_or_error"
    if state == "NODE_FAIL":
        return "infra_fail"
    return "other"


def n_star_table(cost_per_molecule_s: float, budgets_core_h: List[int]) -> List[Dict[str, float]]:
    """Affordable corpus size N* = B / cost, for each budget B (core-hours)."""
    cost_h = cost_per_molecule_s / 3600.0
    out = []
    for b in budgets_core_h:
        out.append({"budget_core_h": b, "n_star": (b / cost_h) if cost_h > 0 else float("inf")})
    return out


def build_records(
    sacct: Dict[int, Dict[str, object]],
    names: Dict[int, str],
    log_dir: Optional[Path],
) -> List[Dict[str, object]]:
    records = []
    for idx in sorted(sacct):
        rec = sacct[idx]
        name = names.get(idx, f"idx{idx}")
        state = str(rec.get("state", "UNKNOWN"))
        sum_g, max_g = (None, None)
        if log_dir is not None:
            sum_g, max_g = parse_log_graphs(log_dir, idx, name)
        records.append(
            {
                "idx": idx,
                "name": name,
                "state": state,
                "bucket": classify(state),
                "elapsed_s": rec.get("elapsed_s"),
                "max_rss_mb": (rec["max_rss_kb"] / 1024.0) if rec.get("max_rss_kb") else None,
                "req_mem": rec.get("req_mem"),
                "sum_graphs": sum_g,
                "max_round_graphs": max_g,
            }
        )
    return records


def summarize(records: List[Dict[str, object]], budgets_core_h: List[int]) -> Dict[str, object]:
    buckets: Dict[str, List[Dict[str, object]]] = {}
    for r in records:
        buckets.setdefault(str(r["bucket"]), []).append(r)

    finished = [r for r in records if r["bucket"] == "finished" and r["elapsed_s"]]
    censored = [r for r in records if r["bucket"] == "censored_timeout" and r["elapsed_s"]]
    fin_costs = sorted(float(r["elapsed_s"]) for r in finished)

    def _stats(xs: List[float]) -> Dict[str, float]:
        if not xs:
            return {}
        return {
            "n": len(xs),
            "mean_s": statistics.fmean(xs),
            "median_s": statistics.median(xs),
            "min_s": min(xs),
            "max_s": max(xs),
            "p90_s": xs[int(0.9 * (len(xs) - 1))],
        }

    # Optimistic: finishers only. Lower-bound-aware: also credit censored tasks
    # their (right-censored) elapsed, which is itself a lower bound on their cost.
    fin_mean = statistics.fmean(fin_costs) if fin_costs else 0.0
    mixed = fin_costs + sorted(float(r["elapsed_s"]) for r in censored)
    mixed_mean = statistics.fmean(mixed) if mixed else 0.0

    return {
        "n_tasks": len(records),
        "bucket_counts": {k: len(v) for k, v in sorted(buckets.items())},
        "censored_fraction": (len(censored) / len(records)) if records else 0.0,
        "finished_cost": _stats(fin_costs),
        "cost_per_molecule_s": {
            "finishers_only_mean": fin_mean,
            "with_censored_lower_bound_mean": mixed_mean,
        },
        "n_star_finishers_only": n_star_table(fin_mean, budgets_core_h),
        "n_star_with_censored_lb": n_star_table(mixed_mean, budgets_core_h),
        "note": (
            "cost unit = wall-clock seconds (sacct). TIMEOUT tasks are right-censored "
            "at their elapsed, so both means are lower bounds and every N* is an upper "
            "bound on the affordable full-enumeration corpus. Graph counts are diagnostic "
            "only and do not predict cost."
        ),
    }


def write_csv(records: List[Dict[str, object]], path: Path) -> None:
    cols = [
        "idx", "name", "state", "bucket", "elapsed_s", "max_rss_mb",
        "req_mem", "sum_graphs", "max_round_graphs",
    ]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in sorted(records, key=lambda x: (x["elapsed_s"] is None, -(x["elapsed_s"] or 0))):
            w.writerow({c: r.get(c) for c in cols})


def _load_sacct_text(args: argparse.Namespace) -> str:
    if args.sacct_file:
        return Path(args.sacct_file).read_text()
    fmt = "JobID,State,ElapsedRaw,MaxRSS,ReqMem"
    out = subprocess.run(
        ["sacct", "-j", args.job_id, "--format", fmt, "-P", "-n"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def main() -> None:
    p = argparse.ArgumentParser(description="MØD cost / N* crossover analysis (feasibility study).")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--sacct-file", help="Pipe-delimited sacct dump (JobID|State|ElapsedRaw|MaxRSS|ReqMem).")
    src.add_argument("--job-id", help="SLURM array job id to query via sacct.")
    p.add_argument("--manifest", required=True, help="name<TAB>smiles manifest the array indexed.")
    p.add_argument("--log-dir", help="Dir of <idx>__<name>.out task logs (for graph-count diagnostics).")
    p.add_argument("--out-dir", required=True, help="Where to write cost_per_molecule.csv + cost_summary.json.")
    p.add_argument("--budgets-core-h", type=int, nargs="+", default=DEFAULT_BUDGETS_CORE_H)
    args = p.parse_args()

    sacct = parse_sacct(_load_sacct_text(args))
    names = parse_manifest(Path(args.manifest))
    log_dir = Path(args.log_dir) if args.log_dir else None

    records = build_records(sacct, names, log_dir)
    summary = summarize(records, args.budgets_core_h)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(records, out_dir / "cost_per_molecule.csv")
    (out_dir / "cost_summary.json").write_text(json.dumps(summary, indent=2))

    bc = summary["bucket_counts"]
    fc = summary["finished_cost"]
    print(f"Cost: {summary['n_tasks']} tasks {bc}")
    if fc:
        print(
            f"  finisher wall: mean={fc['mean_s']/3600:.2f}h median={fc['median_s']/3600:.2f}h "
            f"p90={fc['p90_s']/3600:.2f}h max={fc['max_s']/3600:.2f}h (n={fc['n']})"
        )
    print(f"  censored (timeout) fraction: {summary['censored_fraction']:.1%}")
    print(f"  wrote {out_dir/'cost_per_molecule.csv'} and {out_dir/'cost_summary.json'}")


if __name__ == "__main__":
    main()
