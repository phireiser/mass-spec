# Mechanism-Derived Rule Library — A/B Against the Hand-Authored Rules

`src/data_generation/rules` is hand-authored from the IMS textbook: generalized
templates with `_A`-style placeholders and `§`-extensions, written by a chemist.
`src/data_generation/mechanisms` is the alternative — rules *compiled* from the
curated mechanism corpus in `data/mechanisms/records`, so that adding a book
example to the corpus adds a rule without anyone hand-writing a template.
`main.py --rule-source mechanisms` selects it. This document records how the two
compare and what had to change to make the compiled library competitive.

The measurements here are the reason the document exists: they live in
`data/outputs/metrics/**` and `data/processed*/`, both gitignored, so they do not
survive a fresh clone. Cite these tables, not the directories.

> **Correction (2026-09-25).** Every "legacy 0.360" in §§1, 7, 8 and 9 below was
> measured while the `§` rule-extension machinery was silently dead (see §10).
> The hand-authored arm was firing ionization indiscriminately, which inflated
> both its explained intensity and its null. Re-measured on the same 172
> molecules with `§` working, **legacy's ceiling is 0.268, not 0.360**. The
> mechanism-arm numbers in those sections are unaffected *relative to each
> other* — they were all produced under the same broken `§` — but the compiled
> library's ionization rules also carry `§`, so its absolute figures move too
> (0.277 → 0.256). §10 carries the first clean pair; treat it, not §1, as the
> current standing comparison.

## 1. The result that motivated everything below

Measured 2026-08-23/25 on the same 172 molecules, same config and seed, scored
with `run/analysis/ceiling.sh` (see [FEASIBILITY.md](FEASIBILITY.md) for what the
ceiling is and how the null subtraction works):

| | legacy hand-authored | mechanisms (concrete) |
|---|---|---|
| raw intensity explained (τ = 0.01) | 0.583 | 0.272 |
| null-subtracted ceiling, mean | 0.360 | 0.200 |
| distinct MØD masses per molecule | 30.8 mean, 14 median | 4.4 mean, 3 median |
| molecules with ≤ 3 masses | 16% | 72% |

Mechanism rules produced fewer masses on 140 of the 172 molecules and more on 1.
At 3 masses you are seeing **ionization products only** — and ionization comes
from the legacy library in both arms (`mechanisms/__init__.py` explains why), so
the reading is that the 517 compiled fragmentation rules barely fired at all.

Source files, if they still exist in this working tree:
`data/outputs/metrics/ceiling_summary.json` (legacy arm, Aug 23) and
`data/outputs/metrics/ceiling_mechanisms_2026-08-24/ceiling_summary.json`.
The legacy arm is identified by its date and `run_ceiling.py`'s default
`--fwd-dir`; it carries no explicit label, so re-confirm before publishing.

## 2. Why the concrete library underfires

Each compiled rule was the **full, concrete graph of one book example** — every
spectator atom, and every unchanged hydrogen expanded into an explicit vertex.
MØD matches a rule's left graph by subgraph embedding, so such a rule fires only
where a host contains that entire substructure: in practice, only on the book's
own example compound. The hand-authored rules generalize because a human wrote
the placeholders in; the compiled ones had no such step.

## 3. The two generalization levers

`src/data_generation/mechanisms/generalize.py` prunes each step to the chemistry
it actually performs — the graph diff between the two sides, unioned with the
curated `electron_moves` arrows, plus Steiner connectors, an ion anchor and a
context shell. Two flags on `write_generated_rules.py` expose it:

- `--context-radius N` — keep the reacting core, the paths connecting its parts,
  and an `N`-bond shell of surrounding heavy-atom context. `0` is the bare core;
  a radius past the molecule's diameter reproduces the original.
- `--no-spectator-hydrogens` — write only hydrogens that *move*, so a step drawn
  on a methyl also matches a methylene.

Defaults (neither flag) reproduce the concrete rules byte for byte. MØD accepts
every generalized rule, with the same 13 skips as the concrete library.

## 4. Library size and generality across the sweep

`rules` counts what survives isomorphic deduplication — examples of the same
reaction class collapse onto one rule once their spectator context is pruned.
"written" is mean atoms per rule, i.e. how much a rule insists on.

| config | rules | mean core atoms | mean written | mean pruned |
|---|---:|---:|---:|---:|
| concrete (no flags) | 517 | — | 22.5 | 0 |
| `--no-spectator-hydrogens` alone | 517 | — | 9.1 | 0 |
| `-r 0 --no-spectator-hydrogens` | 246 | 4.1 | 6.0 | 4.1 |
| `-r 1 --no-spectator-hydrogens` | 391 | 3.7 | 7.4 | 2.4 |
| `-r 2 --no-spectator-hydrogens` | 431 | 3.6 | 8.2 | 1.5 |
| `-r 3 --no-spectator-hydrogens` | 447 | 3.6 | 8.7 | 1.0 |
| `-r 4 --no-spectator-hydrogens` | 450 | 3.6 | 9.0 | 0.7 |
| `-r 0` (hydrogens kept) | 384 | 3.7 | 11.1 | 4.1 |
| `-r 1` (hydrogens kept) | 429 | 3.6 | 15.9 | 2.5 |
| `-r 2` (hydrogens kept) | 439 | 3.6 | 18.8 | 1.5 |

## 5. Enumeration cost — generality is not free

Forward pass only (`--skip-backward`), one thread, one molecule per cell, as
`<wall time> / <largest round's graph count>`. `TIMEOUT` is a 600 s cap.
MØD's cost is superlinear in how much each rule matches, which is exactly what
generalization increases (`docs/PHASE2_PLAN.md` Stage 0).

| config | acetone | diethyl ether | 2-heptanone |
|---|---|---|---|
| concrete | 3 s / 11 | 3 s / 16 | 6 s / 72 |
| `-r 0 --no-spectator-hydrogens` | 37 s | 184 s | TIMEOUT (4242 @ round 3) |
| `-r 1 --no-spectator-hydrogens` | 3 s / 35 | 2 s / 25 | TIMEOUT (4400) |
| `-r 2 --no-spectator-hydrogens` | 3 s / 18 | 2 s / 25 | TIMEOUT (2932) |
| `-r 3 --no-spectator-hydrogens` | 3 s / 18 | 3 s / 25 | TIMEOUT (2432) |
| `-r 4 --no-spectator-hydrogens` | 3 s / 18 | 3 s / 25 | 345 s / 4638 |
| `--no-spectator-hydrogens` alone | 3 s / 13 | 3 s / 25 | TIMEOUT (627) |
| `-r 0` (hydrogens kept) | 8 s / 191 | 219 s / 1392 | TIMEOUT (1931) |
| `-r 1` (hydrogens kept) | 3 s / 11 | 3 s / 16 | **7 s / 165** |
| `-r 2` (hydrogens kept) | 3 s / 11 | 3 s / 16 | **5 s / 91** |

The row that matters is `--no-spectator-hydrogens` **alone**, with the full
concrete heavy-atom skeleton: 64 / 198 / 627 graphs over 2-heptanone's first
three rounds, against the concrete library's 38 / 53 / 57. Dropping the
hydrogen constraints — not pruning heavy spectators — is what makes enumeration
explode. That inverts the obvious reading of the generality table in §4: the
flag with the largest effect on mean-atoms-written is the one to leave off.

Keeping hydrogens while pruning heavy spectators stays affordable on larger
molecules too:

| config | capric acid (12) | phenylalanine (12) | stearic acid (20) | cholesterol (28) |
|---|---|---|---|---|
| concrete | 16 s / 111 | 4 s / 60 | 34 s / 73 | 197 s / 189 |
| `-r 1` (hydrogens kept) | 32 s / 427 | 4 s / 63 | 34 s / 199 | 221 s / 514 |
| `-r 2` (hydrogens kept) | 11 s / 142 | 4 s / 60 | 25 s / 75 | 115 s / 227 |

`-r 1` is the chosen configuration: on the four molecules above it costs
within ~2x of the concrete library while producing 2-4x the graphs, and it is
the most general setting that stays affordable. `-r 0` was rejected on cost
(it explodes on diethyl ether, a five-heavy-atom molecule), and every
`--no-spectator-hydrogens` variant was rejected for the reason given above.

## 6. Reproducing a library

```bash
# The chosen configuration: prune heavy spectators to a 1-bond shell,
# keep the hydrogen constraints that hold enumeration cost down.
bash run/setup/write_generated_rules.sh --context-radius 1 \
    --out /app/data/outputs/mech_libs/gen_r1h.py
```

Run an A/B arm on it without touching the committed concrete
`generated_rules.py` (`data_gen.sh` bind-mounts the named file over the
container's copy):

```bash
GENERATED_RULES_FILE=data/outputs/mech_libs/gen_r1h.py \
  PROCESSED_DIR_OVERRIDE=data/processed_mech_r1h \
  bash run/hpc/data_gen_mechanisms.sh

bash run/analysis/ceiling.sh \
  --fwd-dir /app/data/processed_mech_r1h/fwd \
  --out-dir /app/data/outputs/metrics/ceiling_mech_r1h
```

## 7. Corpus A/B of the chosen configuration

Full 172-molecule corpus, `--context-radius 1` with hydrogens kept (429 rules),
generated 2026-09-18 into `data/processed_mech_r1h` and scored into
`data/outputs/metrics/ceiling_mech_r1h`. All 172 SLURM tasks completed; none
failed, timed out or ran out of memory.

| | legacy | mechanisms (concrete) | mechanisms (`-r 1`) |
|---|---|---|---|
| raw intensity explained (τ = 0.01) | 0.583 | 0.272 | **0.349** |
| null-subtracted ceiling, mean | 0.360 | 0.200 | **0.254** |
| null-subtracted ceiling, median | 0.390 | 0.115 | **0.194** |
| formula null, mean | 0.223 | 0.072 | 0.095 |
| distinct MØD masses/molecule | 30.8 mean, 14 median | 4.4 mean, 3 median | 7.5 mean, 4 median |
| molecules with ≤ 3 masses | 16% | 72% | 47% |

Against the concrete library, generalization produced **more** masses on 77
molecules, the same number on 95, and fewer on **none** — the improvement is
monotone, as it should be, since pruning a rule can only relax its match
condition and deduplication only removes rules that had become redundant.

Two conclusions:

1. **Generalization works and is worth keeping.** It closes roughly a third of
   the concrete library's gap to the hand-authored rules (ceiling 0.200 → 0.254
   against legacy's 0.360) for a cost within ~2x, and the share of molecules
   explained by ionization products alone drops from 72% to 47%.
2. **It is not, on its own, enough.** The compiled library still explains
   substantially less than the hand-authored one, and still produces a quarter
   of its distinct masses. Pruning spectator context was necessary but did not
   turn out to be sufficient, and the radius axis is already at its affordable
   end: radius 0 prunes more and so would fire more, but §5 shows it does not
   finish on a five-heavy-atom molecule. Whether radius 0 would close more of
   the gap is therefore untested, not ruled out — it is simply not measurable
   at this enumeration cost.

The open question this leaves is *what kind* of generality the hand-authored
rules have that pruning cannot recover. Their `_A`-style placeholders match an
atom by role rather than by element, which no amount of pruning a concrete
example reproduces: a pruned rule still names carbon where the hand rule says
"any heavy atom". Section 8 tests that.

## 8. Role placeholders on the context shell

A pruned rule still names the element the book example drew at every surviving
position. The hand-authored rules do not: `rules/benzylAllyl_ringGeneral.py`
writes `[_A]1[C]2[C]3:[C]4:...`, where `[_A]` is a placeholder bound per
molecule to the occurring elements by `utils.constrain.apply_constraints`.
Note it also carries **no hydrogens at all**.

Two independent flags reproduce each half of that idiom, both acting only on the
context shell (`keep_set(radius) - keep_set(0)`, ~1.9 positions per rule, which
by construction excludes the reacting core, the Steiner connectors and the ion
anchor — everything radius 0 keeps is load-bearing and keeps its element):

- `--placeholder-context` — write the shell as `[_A]` instead of its element.
- `--bare-context-hydrogens` — drop the shell's unchanged hydrogens, so the
  position stops pinning a substitution pattern. The per-atom form of
  `--no-spectator-hydrogens`.

Cost, measured as in §5, all on top of `--context-radius 1`:

| shell treatment | rules | acetone | diethyl ether | 2-heptanone |
|---|---:|---|---|---|
| none (the §7 library) | 429 | 3 s / 11 | 3 s / 16 | 7 s / 165 |
| `--placeholder-context` | 442 | 2 s / 11 | 3 s / 19 | **9 s / 219** |
| `--bare-context-hydrogens` | 390 | 3 s / 11 | 2 s / 16 | TIMEOUT (1050) |
| both (the hand-rule idiom) | 389 | 3 s / 11 | 4 s / 59 | TIMEOUT (1326) |

**The hydrogen half is again the whole cost, and this time at only ~1.9
positions per rule.** That is the same finding as §5, now isolated: it is not
the *number* of unconstrained positions that matters but that they are
unconstrained in hydrogen. Relaxing the element is close to free — 433 rules
cost what 429 did — while relaxing the hydrogens at a couple of peripheral
positions is enough to stop 2-heptanone finishing in 600 s.

The two levers are also clearly multiplicative rather than additive: alone, the
element placeholder adds ~18% more graphs and the hydrogen drop adds enough to
time out; together they produce 59 graphs on diethyl ether where either alone
produces 16-19.

So only `--placeholder-context` is affordable, and it is a limited effect: a
placeholder that still carries three explicit hydrogens means "any heavy atom
with exactly three hydrogens", which is a methyl by another name. That is
precisely why the hand rules write the position bare — and why this lever
cannot, on its own, recover what they have.

### One variable per position, not one per rule

The first implementation gave every shell position in a rule the same name,
`[_A]`. That is wrong, and the corpus is what caught it: the nominally *more*
general library scored **worse** than plain radius 1 — ceiling 0.235 against
0.254, 6.3 distinct masses per molecule against 7.5, and fewer masses on 28
molecules against more on 12, the losses concentrated in long-chain fatty
acids (stearic acid 66 → 8 masses).

`term_transfers.encode_vertex_label` keeps distinct placeholder names as
independent term *variables*, which means a shared name is not shorthand — it
is an equality constraint. Every position labelled `_A` in one rule must bind
the same element:

```
[_A]1(...)[O+]3([_A]2(...))...     # both shells forced to one element
[_A]1(...)[O+]3([_B]2(...))...     # independent, what the rule actually means
```

245 of 433 rules carried two or more shell positions, so most of the library
was affected. Where a book example drew different elements in its own shell,
the rule stopped matching the very example it was compiled from — a constraint
strictly tighter than the concrete rule it replaced, which is how a
generalization can lose ground. Naming positions `_A`, `_B`, `_C`, ... by
sorted atom id fixes it, and `apply_constraints` already splices one
`constrainLabelAny` block per distinct name.

The general lesson: in term mode a placeholder name is a variable, so reusing
one silently couples the positions that share it. The hand-authored
`rules/migration.py` documents the same trap from the other direction — it is
authored in GML precisely *because* it needs two independent variables.

### Corpus A/B

Full corpus, `--context-radius 1 --placeholder-context` (442 rules), all 172
SLURM tasks completed with no failures. `data/processed_mech_r1hpv`, scored
into `data/outputs/metrics/ceiling_mech_r1hpv`. The shared-`_A` arm is kept in
the table because a generalization scoring *below* its own baseline is the
signal that found the bug:

| | legacy | concrete | `-r 1` | `-r 1` + shared `_A` | `-r 1` + `_A`/`_B` |
|---|---|---|---|---|---|
| raw intensity explained | 0.583 | 0.272 | 0.349 | 0.324 | **0.380** |
| ceiling, mean | 0.360 | 0.200 | 0.254 | 0.235 | **0.277** |
| ceiling, median | 0.390 | 0.115 | 0.194 | 0.166 | **0.229** |
| formula null, mean | 0.223 | 0.072 | 0.095 | 0.090 | 0.103 |
| masses/molecule, mean | 30.8 | 4.4 | 7.5 | 6.3 | **8.3** |
| molecules with ≤ 3 masses | 16% | 72% | 47% | 50% | **44%** |

With independent variables the improvement is monotone again — more masses on
49 molecules, the same on 123, fewer on **none** — which is the property a
pure relaxation must have, and which the shared-`_A` arm visibly violated.

Cumulatively the compiled library has gone 0.200 → 0.254 → 0.277 against the
hand-authored 0.360, i.e. **about half the original gap is now closed**, at a
cost still within ~2x of the concrete library.

## 9. Where this leaves the compiled library

Three generality levers have now been measured, and they rank cleanly by
cost-effectiveness:

| lever | ceiling | cost |
|---|---|---|
| prune spectator context to a 1-bond shell | 0.200 → 0.254 | ~2x |
| stop naming the shell's element (`[_A]`/`[_B]`) | 0.254 → 0.277 | ~free |
| stop writing the shell's hydrogens | untested at corpus scale | unaffordable |

The unifying finding across §5 and §8 is that **hydrogen constraints are what
keep MØD's enumeration tractable.** Relaxing them explodes the derivation graph
whether it is done library-wide (§5) or at ~1.9 peripheral positions per rule
(§8); relaxing element identity is close to free. That is the practical budget
for this rule library, and it is also why the remaining gap to the
hand-authored rules is not simply a matter of turning more levers on: those
rules are a few dozen very general templates, while this library is ~440, and
cost scales with generality × rule count.

The next thing worth testing is therefore not another generality lever but
whether the compiled library can be made *smaller* — collapsing the ~440 rules
onto the reaction classes they are drawn from would buy the budget to write
the remaining positions bare, the way the hand rules do.

## 10. The `§` extension was dead, and the first clean A/B

Every comparison above was run against a hand-authored library whose
`§`-extensions did nothing. Two independent defects, both fixed on
`structure-elucidation`:

1. **The traversals never left their start vertex** (`87109f4`). `collect_bfs`
   and `saturated_path` in `utils/traversal.py` built their neighbour adjacency
   from the *built* graphs while keying visited-sets off the *term* graphs. The
   two key spaces never intersected, so `collect_bfs` returned only its own
   start label and `saturated_path` returned `False` even for directly bonded
   atoms. Both predicates had therefore been inert for the entire history of
   the repository, and every `§R`/`§Y`/`§S` annotation with them.
2. **`§Y` tested the wrong atoms** (`3024d22`). Once the traversal worked, `§Y`
   evaluated the whole BFS-collected subgroup rather than the annotated
   position. On a one-atom rule like `broad_ionization` the "substituent" is the
   entire molecule, so a single carbon anywhere vetoed the derivation. `§Y` now
   constrains only the atom it names. The same commit fixed three mis-indexed
   annotations (`IMS_bookCover.py` ×2, `IMS_chap4_examples.py` ×1) that pointed
   at the wrong DFS position.

`§` indices are **1-based positions of appearance** in the rule's DFS string
(`utils/rule_extention.py` subtracts one and looks the vertex up in
`match.domain`), *not* the numeric labels written in the DFS. `mod.Rule.fromDFS`
renumbers vertices by order of appearance and ignores those labels, which is
what made the three mis-indexed annotations easy to write and invisible to read.

### What the fix cost the legacy arm

| | legacy, `§` dead | + traversal fix | + `§Y` per-atom |
|---|---|---|---|
| null-subtracted ceiling, mean | 0.360 | 0.292 | **0.268** |

The drop is the point: with `§` inert, `broad_ionization` ionized carbon and
hydrogen as readily as heteroatoms, so legacy's 0.360 included spurious mass.
The M+• recovery rate is unchanged at 0.977, because `ei_molecular_ion` carries
no `§`.

### The clean pair

Both arms regenerated and scored under the same fixed code, same 172 molecules,
same seed. `data/processed_legacy_sgY` / `data/processed_mech_sgY`, scored into
`data/outputs/metrics/ceiling_{legacy,mech}_sgY`. All 344 SLURM tasks completed.

| | legacy | mechanisms (`-r 1` + `_A`/`_B`) |
|---|---|---|
| raw intensity explained (τ = 0.01) | 0.395 | 0.336 |
| null-subtracted ceiling, mean | **0.268** | **0.256** |
| null-subtracted ceiling, median | 0.221 | 0.204 |
| formula null, mean | 0.127 | 0.080 |
| distinct MØD masses/molecule | 16.4 mean, 8 median | 6.7 mean, 4 median |
| molecules with ≤ 3 masses | 32% | 49% |
| M+• recovered | 0.977 | 0.977 |

Paired over the 172 molecules, legacy − mechanisms is **+0.011 mean, +0.000
median**; legacy scores higher on 81, the compiled library on 51, with 40 ties
(two-sided sign test p = 0.011). So the hand-authored library still wins, but
the margin is now roughly one part in twenty of the ceiling rather than the
0.160 of §1.

Read this honestly: **most of the closure came from legacy falling, not from the
compiled library rising.** The compiled library moved 0.200 → 0.277 by
generalization and then back to 0.256 when its own ionization rules started
obeying `§`; legacy moved 0.360 → 0.268 by having its rules finally enforced.
The two libraries are now close because the hand-authored one is being measured
correctly for the first time.

Note also how the arms differ in *shape*: legacy explains more raw intensity
(0.395 vs 0.336) but carries a much larger formula null (0.127 vs 0.080),
because it produces 2.4× as many distinct masses. After null subtraction those
two effects nearly cancel. A comparison on raw explained intensity alone would
overstate legacy's advantage by a factor of five.

### `§` coverage audit

Scanning all 173 `fromDFS` rules structurally, and cross-referencing
`data/mechanisms/rule_index.json` against the curated equations:

- **Two `§` annotations are currently defeated by an unannotated duplicate.**
  `IMS_4_12_1`/`IMS_4_12_2` carry `§R1`; `IMS_4_15_1_2`/`IMS_4_15_1_1` are
  byte-identical DFS strings with no annotation, and all four are live in the
  136-rule fragmentation set. MØD applies the unconstrained twin wherever the
  annotated one is blocked, so `§R1` on 4.12 has no effect. Independently
  corroborated by `data/mechanisms/coverage_report.md`, whose 4.12 and 4.15a
  entries quote the same two strings under different equations.
- **Twelve rules leave a spectator stub unconstrained** where a sibling in the
  same book section constrains the analogous position — most clearly
  `IMS_4_19_1` (`§R1R3Y4`, branch at position 2 open, while its twin
  `IMS_4_19_2` covers it with `R2`) and `IMS_4_22` (no `§` at all, while 4.18,
  4.20 and 4.21 all carry `§R1Y2`).
- **Some over-specificity `§` cannot fix**: `IMS_4_37_rH/_rd` and `IMS_4_38_*`
  hard-code `[O+]` where the book section is "hydrogen rearrangement to a
  saturated *heteroatom*"; the fix is `[_A]` + `§Y`, not an annotation alone.

Not covered by that audit: the 27 rules dropped by the conservation guard, the
GML-authored rules in `migration.py` and `wikipedia.py`, and the 78 rules whose
equation carries no curator note — for those the only source of truth is the
page scan in `data/IMS-Book/pages/`.

The compiled library carries **zero** `§` annotations
(`mechanisms/generated_rules.py`), and cannot carry any today: the record schema
has no per-atom annotation slot and `StrictModel` sets `extra="forbid"`, so
expressing generic positions needs an additive `generic_positions` field on
`MechanismRecord` keyed by atom map, plus a curator pass over 358 records.
