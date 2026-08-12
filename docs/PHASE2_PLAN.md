# Phase 2 — gated data construction, and the road to the forward student

Phase 1 is closed: the MØD forward model identifies the true structure among same-formula
decoys at **top-1 0.500 vs chance 0.229** (lift 2.18x, p=5.7e-14, exact Poisson-binomial over
132 targets at 1340/1340 decoy coverage). Reproduce with `run/analysis/score_forward.sh` then
`analysis/discrimination/compare_gate.py`.

**A note on numbering.** The de-risked order and the original unified plan number phases
differently, and conflating them has already caused confusion here:

| | de-risked order | unified plan |
|---|---|---|
| Phase 1 | true-vs-decoy discrimination gate **(done)** | data + MØD semantics + evaluation contract |
| Phase 2 | **gated data construction** (this document) | selective teacher-DAG construction (RL) |
| Phase 3 | — | ICEBERG-style Generate/Score forward student |

This document uses the **de-risked** numbering. It covers gated data construction *and* the
forward student, because the gate's answer determines what the student can be trained on.

---

## 0. The gate this phase exists to pass

The rule was pre-registered: build the selective/RL teacher **only if** the projected corpus
exceeds `N* ~ B / cost_per_molecule`. Measured today:

| quantity | value |
|---|---|
| store structures with SMILES + measured spectrum | **23,730** |
| corpus build, 172 molecules | 17.9 core-h → 0.104 core-h/mol |
| decoy build, 1,155 molecules, uncapped | 180.7 core-h → 0.157 core-h/mol |
| same, with the ring-topology guard | ~25 core-h → **0.022 core-h/mol** |
| active rules | 135 fragmentation + 15 ionization |

At a 1,000 core-h budget that puts N* between ~10,000 and ~45,000 molecules against 23,730
available. **On today's rule library, with the guard on, the trigger is not met.**

### Why that is a reading, not a conclusion

`N*` is not a constant. It is `N*(|R|, guard)`, and both arguments are moving:

* **The rule library is growing.** 28 rules are currently disabled by the conservation
  guardrail and explicitly flagged for re-authoring; 358 curated mechanism records exist with
  42 more pending. A library at 2x today's size is the expected case, not a hypothetical.
  Cost is **superlinear** in rule count — more rules produce more species, and every later
  step matches the whole rule set against that larger species set — so 2x the rules is
  more than 2x the cost.
* **The guard may come off.** `migration_scope`'s cap is measured *lossy* on saturated
  terpenoids (38 of 83 molecules drop a NIST-observed mass, see `strategy.migration_scope`).
  Any analysis that cannot tolerate that runs guard-off, where the same 83 molecules cost
  164.7 core-h instead of 9.2 — an **18x** multiplier on the affected class.

Either shift alone can push `N*` below the corpus. So the RL teacher is **dormant, not
cancelled**, and Stage 0 produces a cost model rather than a single number so the gate can be
re-evaluated cheaply whenever the library changes.

### The constraint that actually binds

Not CPU. **Disk.** 1,426 dumps already occupy 45 GB; per-dump `.pkl` is mean 15.9 MB but
heavy-tailed (median 1.2, p99 375, max 727 MB). Naive scaling to 23,730 molecules is 0.8-3 TB
of `.pkl` + `.dmp` against 28 TB free. Survivable, but it is the thing to design around —
see Stage 1, which stores events instead of dumps.

---

## Stage 0 — a cost model, not a number

Stratified probe: ~200 store molecules sampled across heavy-atom deciles, built with the
shipped guard, measuring core-hours **and bytes** against heavy count and cyclomatic number.

Then two sensitivity arms, because these are the parameters the gate is a function of:

* **rule count** — rebuild a fixed molecule subset at 25/50/75/100% of the rule library
  (random subsets, fixed seed) and fit cost vs `|R|`. This is what converts "the library is
  growing" into a predicted `N*`.
* **guard state** — already measured at one point (18x on 83 molecules); extend to the
  stratified sample so the multiplier is known corpus-wide rather than on terpenoids alone.

Deliverable: `cost(n_heavy, cyclomatic, |R|, guard) -> core-h, bytes`, and `N*` as a function
of the same, written to `data/outputs/metrics/cost_model.json`.

**Pre-register the decision rule before fitting:**

> Activate the RL teacher branch (Stage 2b) when the projected full-enumeration cost of the
> target corpus exceeds the compute budget by more than 2x under the *then-current* rule
> library and guard state.

*Exit:* a defensible `N*`, a recorded activate/defer decision, and a re-runnable script so the
decision can be refreshed rather than re-derived.

---

## Stage 1 — freeze the contract and the event representation

These are unified-Phase-1 exit checks that were never completed, and everything downstream
blocks on them.

* **`FragmentState` / `BreakEvent` extraction** from a dump into compact tensors.
  `FragmentState(state_id, graph, root_atom_ids, formula, exact_mass, charge, radical, depth,
  n_broken_bonds)`; `BreakEvent(event_id, parent_state_id, child_state_ids, rule_id,
  rule_match_id, removed_root_atom_ids, n_broken_bonds_delta)`.
  Two traps to pin with tests: sibling products of one rule application form **one**
  BreakEvent, and `n_broken_bonds` is the boundary cut in M, **not** DAG depth.
* **Sparse DAGs are first-class from day one.** Every record carries
  `provenance ∈ {full, greedy, imitation, rl}` and validates as a legal subgraph of the MØD
  derivation. *This is the entire architectural cost of keeping the RL branch open, and it is
  near-free now and expensive to retrofit.* A schema that assumes full enumeration would have
  to be rewritten the moment Stage 2b activates.
* **Keep events, discard dumps.** The event representation is orders of magnitude smaller than
  the `.pkl`; this is the answer to the disk constraint. Keep dumps only for a pinned
  regression subset.
* **Scaffold-disjoint train/val/test split**, frozen and versioned. Val is for model
  selection; test carries the Phase-1 gate and is opened once.
* **Serialized `BinningSpec`** — integer m/z, sqrt-intensity, L2. Already the de facto contract
  in `analysis/discrimination/spectrum_ops.py`, but not serialized anywhere.

*Exit:* every cached DAG reconstructable from legal MØD events; round-trip test green; splits
provably disjoint; a sparse DAG validates against the same schema as a full one.

---

## Stage 2 — scale the DAG corpus

Build forward DAGs at whatever size Stage 0 justifies, staged 1k → 5k → all, on the existing
`run/hpc/data_gen.sh` array driver.

*Exit:* N DAGs, each recording peak coverage, node count, runtime, rule usage.

### Stage 2b — the RL teacher (dormant branch)

Activated only by Stage 0's pre-registered trigger. Preserved in full because the trigger is
expected to fire as the rule library grows.

State: molecule, observed spectrum, partial DAG, expandable fragment states, legal events,
covered peaks, remaining budget. Action: one legal `BreakEvent`, or STOP.

**Baseline ladder — RL is retained only if it beats the rung below it** at equal node budget:
random legal expansion → greedy weighted-peak-coverage → imitation of greedy → RL, with full
enumeration as the expensive upper reference.

**Known reward-hacking failure mode, to be designed against before the first run:** peak
coverage is monotone in DAG size, so any coverage-rewarding objective converges on never
choosing STOP. The size penalty must be in the objective from the start.

Critical separation to preserve: the teacher-side search **may** use the measured spectrum;
the deployed Generate model **may not**.

*Exit:* sparse DAGs are valid subgraphs; greedy beats random at equal budget; RL retained only
on a pre-registered events-saved/quality bar. Measure **events evaluated**, not wall time.

---

## Stage 3 — Score before Generate

A deliberate reordering of the unified plan, on evidence. The presence-only control
(`score_forward.sh --intensity binary`) scores **top-1 0.477 vs 0.500 weighted, with identical
MRR 0.656** — so the occurrence-count channel, the model's only stand-in for intensity, is
contributing almost nothing. Nearly all current signal is *which* masses are predicted. That
makes intensity the largest untapped channel rather than something already working.

Score also trains on **all** structure-spectrum pairs, including those with no teacher DAG, so
it is not blocked on Stage 2 completing.

The `DecSpecFragment` per-fragment head is already repaired and validated non-collapsing; old
checkpoints no longer load the decoder and must be retrained regardless.

*Baseline to beat, already measured:* top-1 0.500 / MRR 0.656 with occurrence weighting.
*Exit:* learned Score beats occurrence weighting on the **val** split, reported against the
chance baseline, with fragment-order-invariant aggregation and exact synthetic mass-bin tests.

---

## Stage 4 — Generate, both variants

The thesis's headline mechanism-vs-mass contrast.

* **Generate-RuleEvent (primary)** — autoregressive policy over the MØD derivation hypergraph;
  predicts which rule applications lie on the spectrum-explaining path. Rearrangements are
  first-class. Reuses `featurizers/dg_hypergraph.py` + `featurizers/rule.py`.
* **Generate-PerAtom (ICEBERG baseline)** — faithful per-atom-removal model; rearrangements
  handled by contraction. Mass-only, unconstrained inference space.

The contrast is the point: rearrangements such as benzyl→tropylium preserve the heavy-atom set,
so per-atom removal cannot represent them, yet they are real chemical constraints (toluene m/z
65 is only reachable through tropylium). The comparison quantifies what erasing the grammar
costs.

**Known scope limit:** rule embeddings are ID lookups, so Generate does not generalise to
unseen rules. Acceptable for a fixed library; it must be stated as a limitation, and it becomes
blocking if QM rule discovery is ever added.

*Exit:* Generate emits only legal MØD events; overfits a single teacher DAG on demand; never
receives the measured spectrum.

---

## Stage 5 — re-run the Phase-1 gate, once

End to end, on the held-out test split, opened a single time.

**Number to beat: top-1 0.500, lift 2.18x over chance.**

The Phase-1 gate must not enter model selection at any earlier stage — that is what the val
split in Stage 1 is for. Using the test number to pick checkpoints burns the only unbiased
estimate the project has.

---

## Risk register

| risk | mitigation | stage |
|---|---|---|
| `N*` falls below the corpus as the rule library grows | Stage 0 emits a cost model, not a number; RL branch kept live with a pre-registered trigger | 0, 2b |
| Guard-off runs cost 18x on the affected class | guard state is an explicit argument to the cost model | 0 |
| Disk, not CPU, is the binding constraint | store events, discard dumps | 1 |
| Sparse-DAG support retrofitted late | `provenance` + legal-subgraph validation in the schema from day one | 1 |
| Coverage monotone in DAG size → policy never STOPs | size penalty in the objective before the first run | 2b |
| Phase-1 gate leaks into model selection | separate val split, test opened once | 1, 5 |
| Rule embeddings do not generalise to unseen rules | stated scope limit; blocking only for rule discovery | 4 |
