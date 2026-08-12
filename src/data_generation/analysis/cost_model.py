#!/usr/bin/env python3
"""Stage-0 deliverable: build cost as a function of size, rule-library size and guard state.

The selective-teacher gate (``docs/PHASE2_PLAN.md``) fires on ``N* ~ B / cost_per_molecule``,
so a single measured N* is not enough -- it has to be recomputable, because both of its
arguments are moving. The rule library is growing (28 rules pending re-authoring, 358 curated
records) and the migration guard may be switched off for analyses that cannot tolerate its
measured trace losses. This produces ``N*(|R|, guard)`` instead of a number.

Reads the ``/usr/bin/time -v`` block that ``run/hpc/data_gen.sh`` writes into every task log.
That is deliberate: sacct purges accounting after a few days, the logs persist, and the wrapper
sits inside srun specifically so its rusage covers the container rather than the srun client.

Three things this must not get wrong:

* **Censoring is data, not failure.** A task killed at the wall limit means "costs more than
  the limit", which for a gate about affordability is often the most informative observation in
  the sample. Reported explicitly; the naive completed-only mean is a LOWER bound and is
  labelled as such.
* **Equal-n bins must be reweighted.** The probe samples equally per heavy-atom bin to buy
  precision in the expensive tail; the store's real bin frequencies come from the manifest and
  the corpus extrapolation is ``SUM_bin store_count[bin] * mean_cost[bin]``. Averaging the
  sample directly would badly overstate the mean.
* **Disk is a first-class cost.** 1426 dumps already occupy 45 GB with a p99 of 375 MB, so
  bytes are extrapolated alongside core-hours.

    python src/data_generation/analysis/cost_model.py \\
        --arm main=<logdir>,data/processed_cost0 \\
        --arm r25=<logdir>,data/processed_cost0_r25 \\
        --arm noguard=<logdir>,data/processed_cost0_noguard
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Dict, List, Optional

from src.project_paths import shared_name, shared_path

_WALL = re.compile(r"Elapsed \(wall clock\) time.*?:\s*([0-9:.]+)")
_RSS = re.compile(r"Maximum resident set size \(kbytes\):\s*(\d+)")
_NAME = re.compile(r"^mol spectrum of\s+(\S+)", re.MULTILINE)
_SCOPE = re.compile(r"^migration:\s*(.+)$", re.MULTILINE)


def _hms(text: str) -> Optional[float]:
    """`time -v` writes h:mm:ss or m:ss.ss."""
    parts = text.split(":")
    try:
        vals = [float(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 3:
        return vals[0] * 3600 + vals[1] * 60 + vals[2]
    if len(parts) == 2:
        return vals[0] * 60 + vals[1]
    return vals[0] if vals else None


def parse_log(path: Path) -> dict:
    """One task log -> {name, wall_s, rss_gib, censored, capped}."""
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return {}
    name = _NAME.search(text)
    wall = _WALL.search(text)
    rss = _RSS.search(text)
    scope = _SCOPE.search(text)
    return {
        "name": name.group(1) if name else path.stem.split("__", 1)[-1],
        "wall_s": _hms(wall.group(1)) if wall else None,
        "rss_gib": (int(rss.group(1)) / 1048576) if rss else None,
        # No time -v block at all => the step was killed before it could report, i.e. the task
        # hit the wall limit or was OOM-killed. Either way the true cost is above what we saw.
        "censored": wall is None,
        "capped": bool(scope and "CAP" in scope.group(1)),
    }


def arm_rows(log_dir: Path, proc_dir: Path, heavy: Dict[str, int]) -> List[dict]:
    rows = []
    for log in sorted(log_dir.glob("*__*.out")):
        r = parse_log(log)
        if not r:
            continue
        stem = r["name"]
        fwd = proc_dir / shared_name("FWD_DIR_REL")
        pkl = fwd / f"{stem}.pkl"
        dmp = fwd / f"{stem}.dmp"
        r["bytes"] = sum(p.stat().st_size for p in (pkl, dmp) if p.exists())
        r["done"] = (fwd / f"{stem}.done").exists()
        r["nheavy"] = heavy.get(stem)
        rows.append(r)
    return rows


def bin_of(n: int, bins: List[dict]) -> Optional[str]:
    return next((b["bin"] for b in bins if b["lo"] <= n <= b["hi"]), None)


def summarize_arm(name: str, rows: List[dict], bins: List[dict]) -> dict:
    """Per-bin cost, then reweight by the store's real bin frequencies."""
    per_bin: Dict[str, dict] = {}
    for b in bins:
        sel = [r for r in rows if r["nheavy"] is not None
               and bin_of(r["nheavy"], bins) == b["bin"]]
        done = [r for r in sel if not r["censored"] and r["wall_s"] is not None]
        cens = [r for r in sel if r["censored"]]
        if not sel:
            continue
        walls = [r["wall_s"] for r in done]
        byts = [r["bytes"] for r in done if r["bytes"]]
        per_bin[b["bin"]] = {
            "store_count": b["store_count"], "n": len(sel),
            "n_censored": len(cens),
            "mean_wall_s": statistics.fmean(walls) if walls else None,
            "median_wall_s": statistics.median(walls) if walls else None,
            "max_wall_s": max(walls) if walls else None,
            "mean_bytes": statistics.fmean(byts) if byts else None,
            "max_rss_gib": max((r["rss_gib"] for r in done if r["rss_gib"]), default=None),
        }

    # Extrapolate to the whole store. Censored tasks are excluded from the per-bin mean, so
    # this is a LOWER bound whenever any bin censored -- never present it as the estimate.
    core_h = bytes_tot = 0.0
    covered = censored_total = sampled_total = 0
    for b in bins:
        pb = per_bin.get(b["bin"])
        if not pb:
            continue
        sampled_total += pb["n"]
        censored_total += pb["n_censored"]
        if pb["mean_wall_s"] is None:
            continue
        core_h += b["store_count"] * pb["mean_wall_s"] / 3600.0
        bytes_tot += b["store_count"] * (pb["mean_bytes"] or 0)
        covered += b["store_count"]

    all_done = [r for r in rows if not r["censored"] and r["wall_s"] is not None]
    return {
        "arm": name,
        # Per-molecule walls, so arm-vs-arm comparison can be PAIRED rather than a ratio of
        # two differently-censored means (see the scaling block in main()).
        "wall_by_mol": {r["name"]: r["wall_s"] for r in all_done},
        "censored_names": [r["name"] for r in rows if r["censored"]],
        "n_tasks": len(rows),
        "n_censored": censored_total,
        "censoring_rate": censored_total / sampled_total if sampled_total else None,
        "per_bin": per_bin,
        "store_molecules_covered": covered,
        "projected_corpus_core_h": core_h,
        "projected_corpus_tb": bytes_tot / 1024**4,
        "is_lower_bound": censored_total > 0,
        "mean_core_h_per_molecule": (core_h / covered) if covered else None,
        "observed_max_wall_h": max((r["wall_s"] for r in all_done), default=0) / 3600,
        "observed_max_rss_gib": max((r["rss_gib"] or 0 for r in all_done), default=0),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", action="append", default=[], metavar="NAME=LOGDIR,PROCDIR",
                    help="repeatable; NAME is free text, e.g. main / r25 / noguard")
    ap.add_argument("--manifest",
                    default=str(Path(shared_path("METRICS_DIR_REL")) / "cost_probe_manifest.json"))
    ap.add_argument("--budget-core-h", type=float, default=1000.0,
                    help="compute budget B used for N* = B / cost_per_molecule")
    ap.add_argument("--out",
                    default=str(Path(shared_path("METRICS_DIR_REL")) / "cost_model.json"))
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    bins = manifest["bins"]
    heavy = {cas: m["nheavy"] for cas, m in manifest["molecules"].items()}
    store_total = manifest["store_total"]

    arms = []
    for spec in args.arm:
        name, _, paths = spec.partition("=")
        log_dir, _, proc_dir = paths.partition(",")
        rows = arm_rows(Path(log_dir), Path(proc_dir), heavy)
        if not rows:
            print(f"  !! {name}: no task logs under {log_dir}")
            continue
        arms.append(summarize_arm(name, rows, bins))

    if not arms:
        print("no arms parsed")
        return 1

    print(f"store molecules (deduped, with spectrum): {store_total}\n")
    hdr = (f"{'arm':10s} {'tasks':>6s} {'cens':>5s} {'core-h/mol':>11s} "
           f"{'corpus core-h':>14s} {'corpus TB':>10s} {'max wall h':>11s}")
    print(hdr)
    print("-" * len(hdr))
    for a in arms:
        flag = " (LOWER BOUND)" if a["is_lower_bound"] else ""
        print(f"{a['arm']:10s} {a['n_tasks']:6d} {a['n_censored']:5d} "
              f"{a['mean_core_h_per_molecule'] or float('nan'):11.4f} "
              f"{a['projected_corpus_core_h']:14.1f} {a['projected_corpus_tb']:10.2f} "
              f"{a['observed_max_wall_h']:11.2f}{flag}")

    main_arm = next((a for a in arms if a["arm"] == "main"), arms[0])
    print("\nper-bin cost, main arm (store_count x mean = the extrapolation):")
    print(f"  {'bin':8s} {'store':>7s} {'n':>4s} {'cens':>5s} {'median s':>10s} "
          f"{'mean s':>10s} {'mean MB':>9s}")
    for b in bins:
        pb = main_arm["per_bin"].get(b["bin"])
        if not pb:
            continue
        print(f"  {b['bin']:8s} {pb['store_count']:7d} {pb['n']:4d} {pb['n_censored']:5d} "
              f"{(pb['median_wall_s'] or 0):10.1f} {(pb['mean_wall_s'] or 0):10.1f} "
              f"{((pb['mean_bytes'] or 0) / 1048576):9.1f}")

    # --- the gate itself -------------------------------------------------------------
    per_mol = main_arm["mean_core_h_per_molecule"]
    n_star = (args.budget_core_h / per_mol) if per_mol else float("nan")
    print(f"\nN* at B = {args.budget_core_h:.0f} core-h : {n_star:,.0f} molecules"
          f"   (corpus = {store_total:,})")

    # Scaling arms: how N* moves as |R| grows or the guard comes off.
    #
    # PAIRED, and only over molecules that COMPLETED IN BOTH arms. Comparing the arms'
    # reweighted means instead is wrong in a way that inverts the answer: censored tasks are
    # dropped from each arm's mean, an arm that censors more thereby drops more of its own
    # expensive molecules, and the arm that blows up hardest ends up looking CHEAPEST. The
    # first run of this reported guard-off at 0.82x -- i.e. that removing the guard saves
    # time -- purely from that artifact.
    scaling = {}
    for a in arms:
        if a["arm"] == "main":
            continue
        both = [n for n in a["wall_by_mol"] if n in main_arm["wall_by_mol"]]
        num = sum(a["wall_by_mol"][n] for n in both)
        den = sum(main_arm["wall_by_mol"][n] for n in both)
        scaling[a["arm"]] = {
            "ratio": (num / den) if den else None,
            "n_paired": len(both),
            "n_censored_this_arm": a["n_censored"],
            "n_censored_main_on_same_set": sum(
                1 for n in a["censored_names"] if n in main_arm["wall_by_mol"]),
        }
    if scaling:
        print("\ncost multiplier vs the main arm (PAIRED, both-completed molecules only):")
        for k, v in sorted(scaling.items()):
            if v["ratio"] is None:
                continue
            note = (f"  [{v['n_censored_this_arm']} censored here, excluded -> "
                    f"ratio is a LOWER bound]" if v["n_censored_this_arm"] else "")
            print(f"  {k:10s} {v['ratio']:6.2f}x  on {v['n_paired']:3d} paired"
                  f"   -> N* {n_star / v['ratio']:,.0f}{note}")

    # The rule as pre-registered in docs/PHASE2_PLAN.md, stated on COST vs BUDGET:
    #     activate when projected full-enumeration cost > 2 x budget.
    # An earlier version of this line tested `n_star > 2 * store_total`, which is
    # algebraically `cost > B/2` -- four times stricter, and it flipped the verdict to
    # ACTIVATE on data the registered rule defers on. Kept explicit here so the two can never
    # drift apart again.
    projected = main_arm["projected_corpus_core_h"]
    fires = projected > 2 * args.budget_core_h
    verdict = (f"ACTIVATE Stage 2b -- projected {projected:.0f} core-h > 2x budget "
               f"({2 * args.budget_core_h:.0f})" if fires else
               f"DEFER -- projected {projected:.0f} core-h <= 2x budget "
               f"({2 * args.budget_core_h:.0f})")
    print(f"\nprojected full-enumeration cost: {projected:.1f} core-h against B="
          f"{args.budget_core_h:.0f}")
    print(f"  the registered rule fires at B < {projected / 2:.0f} core-h; "
          f"cost merely exceeds B at B < {projected:.0f}")
    print(f"\nPRE-REGISTERED TRIGGER: {verdict}")
    if main_arm["is_lower_bound"]:
        # Censoring only ever pushes measured cost DOWN, so it makes a DEFER weaker and an
        # ACTIVATE stronger. Saying "weaker than it looks" regardless would misread the
        # direction of the bias in exactly the case where the trigger fires.
        print(f"  NOTE: main arm censored {main_arm['n_censored']} tasks, so measured cost is a"
              f" LOWER bound and N* an UPPER bound.")
        print("        " + ("This STRENGTHENS the verdict: the true N* is smaller still."
                            if verdict.startswith("ACTIVATE") else
                            "This WEAKENS the verdict: the true N* is smaller than shown."))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "store_total": store_total, "budget_core_h": args.budget_core_h,
        "n_star": n_star, "scaling_vs_main": scaling, "verdict": verdict,
        "arms": arms,
    }, indent=1))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
