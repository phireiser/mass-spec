# Data Generation Performance

Where the MØD EI-MS fragmentation pipeline (`src/data_generation`) spends its time, which
levers move it, and which do not.

**Re-measured 2026-08-10.** The original version of this document (2026-06-22) concluded
that the `sub_group` `rightPredicate` was 100 % of per-molecule runtime and that the cost
was a fixed floor immune to every lever. That is no longer true — three optimisation
commits landed on exactly that hot path afterwards, and the bottleneck moved. The old
conclusions are preserved in [Superseded](#superseded-the-june-2026-findings) because they
explain why parts of the code look the way they do, but do not act on them.

Numbers are wall-clock, single process, inside `mol-spectro.sif`, `numThreads=1`,
`frag_repeat=5`, migration on (the shipping default) unless stated. Reproduce with
`src/plot/bench_datagen_strategy.py`, one config per process.

## TL;DR

- **The charge-migration model is the cost.** Turning migration off takes anthracene from
  4.89 s to 0.26 s and folic acid from 105 s to 7.7 s. Everything else is rounding.
- **The `sub_group` predicate is now effectively free but still does its job.** It was 100 %
  of runtime in June. It is cheap because the redundant enumeration behind it was removed,
  not because it stopped filtering — it still rejects 15.6 % of cyclohexanol's species.
- Per-molecule cost is no longer a fixed floor. It scales with the species count the
  migration model generates, which is what `migration_scope` exists to bound.
- Small molecules are ~80× faster than this document used to record: **acetone runs the
  full pipeline in 1.53 s**, not ~120 s.
- Throughput is still won by across-molecule parallelism, which the SLURM array already
  provides. The full 172-molecule corpus costs ~17.9 core-hours, and 14 of those are the
  8 steroids.

## Fixed overhead vs. real work

A SLURM task's wall time is not all build. Measured on the login node with a warm image:

| stage | cumulative |
|---|---|
| container start (`python -c pass`) | 0.42 s |
| + `import mod` | 0.65 s |
| + import the rules package (all GML rules built and conservation-checked) | 0.79 s |
| full cold `main.py` run, anthracene | 6.94 s |

So rule loading is ~0.14 s and startup is under a second. On a compute node the same floor
is **~7 s** — carbon monoxide, which fragments to nothing, still takes 7.5 s per SLURM task.
That gap is loading the 8.5 GB SIF over GPFS plus the `srun` chain, not work.

The corpus median SLURM task is 14 s, i.e. roughly half fixed overhead and half build.
Don't read per-task SLURM elapsed as build cost for small molecules.

## Where the time goes

Strategy bisection on anthracene (`species` = DG vertices):

| Configuration | Time | Species |
|---|---|---|
| Ionization only | 0.06 s | 13 |
| + 1 fragmentation round, **unfiltered** | 0.10 s | 74 |
| + 1 round, **mass/charge bounds only** | 0.12 s | 74 |
| + 1 round, **`sub_group` only** | 0.10 s | 74 |
| Full shipping strategy (`repeat[5]`) | **4.89 s** | 2126 |

The single-round rows no longer discriminate: at one round nothing has been rejected yet,
so every filter combination returns the same 74 species. The cost is in the repeat depth,
not in any one filter. Dropping a filter from the *shipping* strategy at full depth is the
informative test:

| molecule | full | minus `sub_group` | minus bounds | `sub_group` calls | species rejected |
|---|---|---|---|---|---|
| acetone | 0.05 s / 29 sp | 0.05 s / 29 sp | 0.04 s / 29 sp | 17 | 0 |
| catechol | 0.77 s / 758 sp | 0.77 s / 758 sp | 0.63 s / 758 sp | 14 | 0 |
| anthracene | 4.82 s / 2126 sp | 4.74 s / 2126 sp | 4.31 s / 2126 sp | 40 | 0 |
| butyric acid | 0.38 s / 298 sp | 0.37 s / 309 sp | 0.33 s / 298 sp | 67 | 11 (3.6 %) |
| **cyclohexanol** | 6.97 s / 2330 sp | — / **2761 sp** | — | **2397** | **431 (15.6 %)** |

`sub_group` costs nothing measurable, but it is **not** inert — whether it rejects anything
is a property of the molecule, not of the predicate. The `§` extensions encode alkyl /
heteroatom / saturated-path context, so they barely fire on aromatics (catechol 14 calls,
anthracene 40) or on a molecule too small to have a saturated framework (acetone 17), and
fire hard on saturated frameworks (cyclohexanol 2397 calls, rejecting 15.6 % of the graph).
Benchmark it on a saturated alicyclic or a chain acid; an aromatic will show you nothing.

### Why it got cheap without getting weaker

Two candidate explanations were tested, because a filter that stops filtering would be cheap
for the wrong reason.

**Did `53872ee`'s `rightLimit=1` weaken the predicate? No — refuted.** Re-running with the
mapper unbounded (`bench_datagen_strategy.py --unbounded-right`, which restores pre-`53872ee`
semantics) gives **identical species *and* derivation counts** on every molecule tried,
including the two where the predicate actually rejects:

| molecule | `rightLimit=1` | unbounded |
|---|---|---|
| cyclohexanol | 2330 sp / 3553 der / 6.97 s | 2330 sp / 3553 der / **11.70 s** |
| butyric acid | 298 sp / 531 der | 298 sp / 531 der |
| valeric acid | 486 sp / 905 der | 486 sp / 905 der |
| 1-propanol | 71 sp / 135 der | 71 sp / 135 der |
| 2-propanol | 44 sp / 81 der | 44 sp / 81 der |
| acetone / alanine | 29 / 165 sp | 29 / 165 sp |

Unbounded is 1.7× slower on cyclohexanol for exactly the same graph. The commit's claim —
that right-side comatch multiplicity cannot change the outcome, because the outcome depends
only on the left map — holds, and it still holds after migration landed. (The interception
was verified rather than assumed: the patched mapper records 67 calls on butyric acid, all
at `right_limit=1`.)

**Did the conservation guardrail reduce what there is to reject? Partly, yes.** `§`-carrying
fragmentation rules went from 65 of 159 in June to **47 of 135** today, and **11 of the 28**
rules the guardrail disables carry a `§`. So the predicate genuinely has less to do than it
did — but that is lost *rule coverage*, a chemistry question tracked with the guardrail, not
a weakening of the predicate itself.

## Levers

Measured on anthracene at the shipping configuration (4.89 s / 2126 species):

| Lever | Result |
|---|---|
| `numThreads` 1 → 4 | 4.89 s → 4.89 s. **Still useless.** A Python `rightPredicate` serialises execution; `--cpus-per-task=1` remains correct. |
| `frag_repeat` 5 → 3 | 4.89 s → 0.90 s, but 2126 → 561 species. **Now a real lever, and lossy** — the June note that acetone saturates by round 3 does not generalise. |
| **migration off** | 4.89 s → **0.26 s**, 2126 → 105 species. On folic acid, 105.2 s → 7.7 s and 10070 → 1225 species. |

Migration is the whole cost curve. It is also where the accuracy gains are (glucose
p=3.7e-05, limonene p=3.3e-04, sucrose p=0.005), so it is not a free win to switch off —
`core/strategy.py:migration_scope` owns that trade-off per molecule and documents the
evidence. Cost control belongs there, not in a global flag.

## What changed since June

Three commits landed on the hot path this document originally described:

- `bcfd88c` (2026-06-22) derive fragment charge/mass from term labels
- `ab4e079` (2026-07-05) dedupe `sub_group` matches by generalized-position signature
- `53872ee` (2026-07-10) cap `DGVertexMapper` `rightLimit=1` in the `sub_group` predicate

The last is precisely the fix the June document listed as "highest potential": it stops MØD
enumerating every vertex mapping to service the Python callback. Together they removed the
predicate from the cost profile **without changing what it accepts** — see
[Why it got cheap without getting weaker](#why-it-got-cheap-without-getting-weaker).

Acetone — the June benchmark — now runs the full pipeline in **1.53 s** and produces the
same 11 final species it produced at ~120 s, so this is genuine optimisation rather than
skipped work.

## Recommendations

1. **Scale by across-molecule parallelism.** Unchanged, and the SLURM array already does it.
   `--cpus-per-task=1` is right; extra threads still do nothing.
2. **Bound cost through `migration_scope`, not through global knobs.** The saturated tail is
   where cost is unbounded, and the multiplicity cap is what makes it buildable (aldosterone:
   1 h14 capped, versus killed at 12 h30 uncapped). Lowering `frag_repeat` corpus-wide would
   be cheaper but drops real fragments.
3. **Re-measure before optimising further.** Every row above was stale within seven weeks.
   `src/plot/bench_datagen_strategy.py` regenerates the tables; run it rather than trusting
   the numbers here.
4. Profiling caveats: `cProfile` misattributes this workload (it points at `graph_from_term`,
   which is per-call profiler overhead — removing those calls moves wall clock by ~0). A
   sampling profiler cannot see into MØD either: 86 % of samples sit in the C++ matching loop
   with no Python frame below it. See `src/plot/profile_datagen_flamegraph.py`.

## Superseded: the June 2026 findings

Kept for provenance. **These no longer reproduce** — see above.

- 100 % of per-molecule runtime was the `sub_group` `rightPredicate`; rule matching, the
  mass/charge bounds, and DG construction were essentially free.
- On acetone: ionization-only 0.0 s / 7 species; +1 unfiltered round 0.0 s / 36 species;
  bounds-only 0.0 s / 36 species; **`sub_group` only 121 s / 11 species**; full pipeline
  ~120 s / 11 species.
- The cost was described as a fixed floor immune to `numThreads` (130.6 → 120.6 s),
  `frag_repeat` 5→3 (130.6 → 119.4 s, same species), rule count 159→79 (125.1 → 122.4 s),
  predicate-body optimisation (122.1 → 120.0 s), and filter reordering (156 → 180 s, worse).
- 65 of 159 fragmentation rules carried a `§` subgroup extension.
- It recommended raising the then 30-minute per-task wall limit, which has since been done
  (now 23 h30).
