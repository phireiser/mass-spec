# Data Generation Performance

Findings from a profiling investigation into why the MØD EI-MS fragmentation
pipeline (`src/data_generation`) is slow, what the real bottleneck is, and which
optimizations help (and — importantly — which do not).

All numbers below are wall-clock, single process, inside the `mol-spectro.sif`
container, on **acetone** (`CC(=O)C`, 11 final species) unless stated otherwise.
Acetone is small enough to complete (~120 s) yet fully exercises the strategy.

## TL;DR

- **100 % of the per-molecule runtime is the `sub_group` chemical-constraint
  `rightPredicate`** (`core/predicates.py`). Rule matching, the mass/charge
  bounds, and derivation-graph construction are essentially free.
- The Python *inside* `sub_group` is ~1 % of the time; the rest is MØD's own
  per-candidate-derivation cost of servicing the predicate.
- The per-molecule cost is a **fixed floor** that does **not** respond to the
  obvious levers (threading, `frag_repeat`, rule count, predicate-body
  optimization, filter reordering — all measured below).
- The only thing that reduces total dataset time today is **across-molecule
  parallelism**, which the SLURM array in `run/hpc/data_gen.sh` already provides.

## Method

The strategy (`core/strategy.py`) is:

```
addSubset(mol)
  >> sub_group(repeat[1](ionization))
  >> charge_bound(amu_bound(sub_group(repeat[frag_repeat](fragmentation))))
```

We timed `dg.build().execute(strat)` under controlled variations, and used
wall-clock accumulators (not cProfile — see the warning below) to attribute time.

## Where the time goes (bisection)

| Configuration | Time | Species |
|---|---|---|
| Ionization only | 0.0 s | 7 |
| Ionization + 1 fragmentation round, **unfiltered** | 0.0 s | 36 |
| 1 fragmentation round, **mass/charge bounds only** (no `sub_group`) | 0.0 s | 36 |
| 1 fragmentation round, **`sub_group` only** | **121 s** | 11 |
| Full pipeline (`repeat[5]`, all filters) | ~120 s | 11 |

Rule matching and the mass/charge bounds are free. **`sub_group` is the entire
cost.** Inside it, `get_rule_2_molecule_maps` accounts for only ~1.6 s / 63 calls
(~1 %); the remaining ~120 s is MØD materializing/evaluating each candidate
derivation so the predicate can inspect it.

## What does NOT help (measured)

| Lever | Result |
|---|---|
| `numThreads` 1 -> 4 | 130.6 s -> 120.6 s (noise). A Python `rightPredicate` forces effectively single-threaded execution. |
| `frag_repeat` 5 -> 3 | 130.6 s -> 119.4 s, same 11 species (acetone saturates at ≤3 rounds). |
| Fragmentation rules 159 -> 79 | 125.1 s -> 122.4 s, same 11 species (cost is not linear in rule count). |
| Term-space charge/mass in predicates; build-once traversal index | 122.1 s -> 120.0 s (bodies are ~1 % of time). |
| Reorder mass/charge bounds before `sub_group` | 156 s -> 180 s (slightly **worse**). |

> **cProfile is misleading here.** It first pointed at `graph_from_term` (551 k
> tiny calls) as the hotspot, but that was per-call profiler overhead; removing
> those calls moved wall-clock by ~0. Always confirm with wall-clock timers.

These results overturned an initial hypothesis ("bump threads + lower
`frag_repeat`"). They do not work — verify before repeating that advice.

## Why `sub_group` is expensive

`sub_group` is a MØD `rightPredicate`. As the **innermost** filter it is invoked
for every candidate derivation MØD generates during the fragmentation `repeat`,
and MØD must materialize each derivation (construct/canonicalize the product
graph in term mode, expose `derivation.rule`/`.left`) before the Python callback
runs. The callback itself is cheap; the per-candidate materialization MØD does to
service it is not, and it dominates even though only 11 species survive.

65 of 159 fragmentation rules carry a `§` subgroup extension (the ones whose
`sub_group` body actually calls `get_rule_2_molecule_maps`).

## Recommendations

1. **Throughput, not per-molecule speed (no code change).**
   The per-molecule cost is a fixed floor; molecules are independent.
   `run/hpc/data_gen.sh` already self-submits as `--array=1-N` with no `%K`
   concurrency cap and `--cpus-per-task=1` (correct — extra threads do nothing).
   Scale by giving the scheduler more nodes/cores.
   - **One real fix:** `--time=0-00:30:00` per task will silently kill molecules
     whose runtime exceeds 30 min (larger molecules -> many more candidate
     derivations -> far slower than acetone). Raise the wall-time ceiling so hard
     molecules complete instead of being dropped from the dataset.

2. **Eliminate the `rightPredicate` from the hot path (highest potential).**
   Re-express the alkyl / heteroatom / saturated-path subgroup conditions as
   native MØD GML rule constraints (`constrainAdj`, `constrainLabelAny`, …) that
   MØD evaluates in C++ during matching, removing the Python predicate MØD spends
   ~120 s servicing. High effort, needs MØD-rule expertise; some conditions may
   not be expressible. Validate against the pinned species set (see Tests).

3. **Attach `sub_group` only to the 65 `§`-rules** (split the rule set so non-`§`
   derivations never enter the predicate). Cheap to prototype, but unproven — the
   rule-count result suggests a few expensive `§`-rules may dominate, so it may
   not pay off.
