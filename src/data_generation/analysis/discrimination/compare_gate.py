#!/usr/bin/env python3
"""Phase-1 gate verdict: forward model vs the oracle bar vs chance, on identical targets.

The two halves of Phase 1 report metrics that look comparable and are not. ``discriminate``
reports a mean **best-decoy cosine** (0.85) and ``score_forward`` reports a **top-1 accuracy**
(0.50); quoting them side by side compares a similarity to a rate. This joins the two
per-target CSVs, restricts to the targets both scored, and reports top-1 accuracy for each --
the same statistic, on the same molecules.

**The chance baseline is the point.** Decoy-set size varies from 1 to 71 across the corpus, so
a raw top-1 rate is uninterpretable on its own: a target with a single decoy is a coin flip,
and the corpus contains many of them. Under random ranking a target with ``n`` decoys is
identified with probability ``1/(n+1)``, so the null is a sum of independent Bernoullis with
*different* success probabilities -- a Poisson-binomial. Its exact distribution is computed
here by convolution (no normal approximation, no sampling), giving an exact one-sided p-value
for "the model identifies more targets than random ranking would".

This matters because the same trap already produced a false positive in this project once: the
steroids' migration TPR gain looked real at 0.810 observed vs 0.793 by chance (p=0.56).

**The oracle's top-1 is degenerate and must not be quoted as the bar.** In the library-match
arm the true candidate is scored by ``cosine(observed, observed) == 1.0``, so it ranks first by
construction and oracle top-1 is 1.000 on every target it scores. The informative oracle number
is its mean *best-decoy* cosine (~0.85) -- how close the nearest wrong structure's measured
spectrum gets -- which is a similarity, not a rate. The rate that means something is the
chance baseline below.

Reads only the two metrics CSVs, so it needs neither ``mod`` nor the container:

    python src/data_generation/analysis/discrimination/compare_gate.py
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List

from src.project_paths import shared_path


def _poisson_binomial(probs: List[float]) -> List[float]:
    """Exact PMF of the number of successes for independent, non-identical Bernoullis."""
    pmf = [1.0]
    for p in probs:
        nxt = [0.0] * (len(pmf) + 1)
        for k, acc in enumerate(pmf):
            nxt[k] += acc * (1.0 - p)
            nxt[k + 1] += acc * p
        pmf = nxt
    return pmf


def _upper_tail(pmf: List[float], observed: int) -> float:
    """P(X >= observed) -- one-sided, so the test asks only 'better than chance'."""
    return sum(pmf[observed:]) if observed < len(pmf) else 0.0


def _load(path: Path, key_fields: Dict[str, str]) -> Dict[str, dict]:
    """Rows keyed by target name, keeping only the fields we compare."""
    out: Dict[str, dict] = {}
    if not path.exists():
        return out
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("status") != "ok":
                continue
            row = {}
            for dest, src in key_fields.items():
                row[dest] = r.get(src, "")
            out[str(r["name"]).strip()] = row
    return out


def _as_bool(v) -> "bool | None":
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return True if s == "true" else False if s == "false" else None


def _as_int(v) -> "int | None":
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _as_float(v) -> "float | None":
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def summarize(arm: str, rows: List[dict]) -> dict:
    """Top-1 accuracy, MRR and the exact Poisson-binomial chance test for one arm."""
    hits = [r for r in rows if r["identified"] is not None]
    n_hit = sum(1 for r in hits if r["identified"])
    # Random ranking puts the true structure first with probability 1/(n_decoys + 1).
    chance = [1.0 / (r["n_decoys"] + 1) for r in hits]
    pmf = _poisson_binomial(chance)
    expected = sum(chance)
    ranks = [r["rank"] for r in rows if r["rank"]]
    return {
        "arm": arm,
        "n_targets": len(hits),
        "n_identified": n_hit,
        "top1": n_hit / len(hits) if hits else float("nan"),
        "top1_chance": expected / len(hits) if hits else float("nan"),
        "expected_identified_by_chance": expected,
        "p_value_one_sided": _upper_tail(pmf, n_hit),
        "mrr": (sum(1.0 / r for r in ranks) / len(ranks)) if ranks else float("nan"),
        "lift_over_chance": (n_hit / expected) if expected else float("nan"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metrics-dir", default=str(shared_path("METRICS_DIR_REL")))
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    mdir = Path(args.metrics_dir)
    oracle = _load(mdir / "discrimination_per_target.csv",
                   {"identified": "identified", "rank": "true_rank", "n": "n_decoys"})
    forward = _load(mdir / "forward_discrimination_per_target.csv",
                    {"identified": "identified_forward", "rank": "true_rank_forward",
                     "n": "n_decoys_scored", "full": "full_coverage"})

    shared = sorted(set(oracle) & set(forward))
    if not shared:
        print("no targets scored by BOTH arms -- run discrimination.sh and score_forward.sh")
        return 1

    o_rows, f_rows, per_target = [], [], []
    for name in shared:
        o, f = oracle[name], forward[name]
        # The comparison is only meaningful where both arms ranked against the same field.
        n_o, n_f = _as_int(o["n"]), _as_int(f["n"])
        if n_o is None or n_f is None or n_o != n_f:
            continue
        o_rows.append({"identified": _as_bool(o["identified"]), "rank": _as_int(o["rank"]),
                       "n_decoys": n_o})
        f_rows.append({"identified": _as_bool(f["identified"]), "rank": _as_int(f["rank"]),
                       "n_decoys": n_f})
        per_target.append({
            "name": name, "n_decoys": n_f,
            "oracle_identified": _as_bool(o["identified"]),
            "forward_identified": _as_bool(f["identified"]),
            "oracle_rank": _as_int(o["rank"]), "forward_rank": _as_int(f["rank"]),
        })

    if not per_target:
        print("no targets where both arms ranked against the same decoy field")
        return 1

    # Headline arm: the forward model over EVERY target it scored, not just the oracle
    # intersection. The intersection is restricted to equal decoy-field size, which is the
    # right control for comparing the two arms but discards ~half the evidence about the
    # forward model itself.
    all_forward = [{"identified": _as_bool(f["identified"]), "rank": _as_int(f["rank"]),
                    "n_decoys": _as_int(f["n"])}
                   for f in forward.values() if _as_int(f["n"])]
    headline = summarize("forward, all scored targets", all_forward)

    arms = [headline,
            summarize("oracle (measured decoy spectra)", o_rows),
            summarize("forward (MOD prediction)", f_rows)]

    both = sum(1 for r in per_target if r["oracle_identified"] and r["forward_identified"])
    only_f = sum(1 for r in per_target if r["forward_identified"]
                 and not r["oracle_identified"])
    only_o = sum(1 for r in per_target if r["oracle_identified"]
                 and not r["forward_identified"])
    neither = len(per_target) - both - only_f - only_o

    hdr = (f"{'arm':34s} {'n':>4s} {'top-1':>7s} {'chance':>7s} {'lift':>5s} "
           f"{'p':>9s} {'MRR':>6s}")
    print(hdr)
    print("-" * len(hdr))
    for a in arms:
        print(f"{a['arm']:34s} {a['n_targets']:4d} {a['top1']:7.3f} {a['top1_chance']:7.3f} "
              f"{a['lift_over_chance']:5.2f} {a['p_value_one_sided']:9.2e} {a['mrr']:6.3f}")
    print(f"\n(rows 2-3 are the matched subset: {len(per_target)} targets where both arms "
          f"ranked against an identical decoy field. Oracle top-1 is 1.000 by construction.)")

    print(f"\nagreement: both {both}   forward-only {only_f}   oracle-only {only_o}   "
          f"neither {neither}")
    fwd = next(a for a in arms if a["arm"].startswith("forward"))
    orc = next(a for a in arms if a["arm"].startswith("oracle"))
    print(f"forward closes {100 * (fwd['top1'] - fwd['top1_chance']) / (orc['top1'] - orc['top1_chance']):.1f}% "
          f"of the chance->oracle gap" if orc["top1"] > orc["top1_chance"] else "")

    out = Path(args.out) if args.out else mdir / "gate_comparison.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"arms": arms, "agreement": {
        "both": both, "forward_only": only_f, "oracle_only": only_o, "neither": neither},
        "per_target": per_target}, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
