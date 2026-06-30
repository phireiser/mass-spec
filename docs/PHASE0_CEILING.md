# Phase 0.1 — MØD Explainability Ceiling

The cheap, no-ML gate for the EI spectrum-to-structure thesis. Before building any
learned model or scaling teacher-DAG construction, it answers: **does the MØD rule
library actually explain the high-intensity peaks in real EI spectra?** If the
ceiling is low, the rule library — not the model — is the bottleneck, and chemistry
must be fixed before modeling.

## What it computes

For every molecule with both a forward MØD dump and a NIST EI spectrum, working at
nominal (unit-resolution, integer) m/z:

- **Explainability ceiling** — the intensity-weighted fraction of high-intensity
  peaks (at m/z ≤ M+•) whose nominal mass MØD produces a charged fragment for,
  **minus a random-formula null**, with a 95% bootstrap CI. The null subtraction is
  essential: at unit resolution a random fragmenter matches peaks by chance, so the
  raw fraction overstates real explanatory power.
  - **Formula-aware null (primary):** sample `|MØD-mass-set|` nominal masses from the
    sub-formulas reachable from the precursor (element counts bounded by the
    precursor, H + 2 for minor transfer, mass ≤ M+•, ≥ 1 heavy atom), weighted by how
    many formulas land on each nominal mass. This controls for real fragment masses
    clustering at certain nominal values.
  - **Uniform null (sanity):** the same, drawing uniformly from `[1, M+•]`. Reported
    alongside. Empirically `null_formula > null_uniform` (≈0.12 vs ≈0.08 on the
    subset): formula-reachable nominal masses concentrate exactly where real fragment
    (and real peak) masses sit, so a formula-plausible random fragmenter matches peaks
    *more* often than a uniform one. That makes the formula-aware null the more
    conservative (higher) bar — which is why it is the primary one.
- **M+• presence** — `mplus_in_spectrum` (is the molecular ion peak in the spectrum?)
  and `mplus_in_mod` (did MØD produce it?). For EI these should both be near 100%.
- **Odd/even-electron split of the unexplained peaks** — each unexplained peak is
  labelled OE or EE by the **nitrogen rule** (nominal-mass parity vs the molecule's
  nitrogen-count parity). A heavy EE skew in the *unexplained* intensity points at
  missing H-rearrangement / even-electron chemistry in the rule set. Heuristic
  caveat: exact only when a fragment keeps a nitrogen count of the same parity as the
  precursor — definitive for the N-free majority, indicative for N-bearing molecules.

A high-intensity threshold τ (fraction of base peak) is swept over
`{0, 0.01, 0.05, 0.10}`; the null-subtracted ceiling uses the primary τ = 0.01.

## Binning contract

Integer / nominal m/z everywhere, binned with **`round`** (not the legacy `int`
truncation used elsewhere in the pipeline), so Cl/Br/S-bearing fragments — whose
monoisotopic mass sits just below the integer — land on the correct nominal peak.

## How to run

> **Prerequisite — dump freshness.** The ceiling is only meaningful on dumps built
> with the current EI ruleset (the one containing `ei_molecular_ion`). The dumps
> shipped under `data/processed/fwd` predate that rule and lack M+•; running on them
> measures the obsolete ruleset (M+• rate ≈ 0 by construction). Regenerate first.

Provisional EI ceiling on a representative, class-spanning subset, on SLURM
(one molecule per array task; a dependent `afterany` job scores the ceiling once
the array finishes). Writes fresh forward DGs to a gitignored `outputs/` dir and
leaves the stale `data/processed/fwd` dumps intact:

```bash
sbatch run/hpc/regen_subset.sh
# array regen -> outputs/phase0/regen_subset/fwd
# dependent ceiling -> outputs/phase0/subset/{ceiling_per_molecule.csv,ceiling_summary.json}
```

Each task is wrapped in `/usr/bin/time -v`, so the per-task logs under
`outputs/logs/regen_subset/slurm/` double as Phase 0.2 per-molecule cost data.

Full corpus (all ~150 molecules that have both a dump and a spectrum):

```bash
sbatch run/hpc/regen_subset.sh --all-with-spectrum
```

> **Cost warning.** Per-molecule cost is dominated by *saturated aliphatic* content,
> not size, and spans ~6000× on the subset (butane C4H10 ~4 h; aromatics seconds).
> The full corpus contains longer saturated chains (pentane … nonane, alkyl acids),
> so expect a heavy tail — keep the wall-time cap generous and treat the result as
> the Phase 0.2 cost distribution (use it for N\* = B / cost, not a mean).

Ceiling on an existing set of (fresh) dumps:

```bash
bash run/analysis/phase0_ceiling.sh                       # full corpus, default dirs
bash run/analysis/phase0_ceiling.sh --names acetone,toluene,aniline --draws 200   # quick
```

Plots (pure pandas/matplotlib):

```bash
python src/plot/plot_phase0_ceiling.py --csv outputs/phase0/subset/ceiling_per_molecule.csv
```

Unit tests for the pure metrics (run bare, no container):

```bash
python3 src/tests/unit_test_ceiling.py
```

## Code

- `src/data_generation/phase0/ceiling_metrics.py` — pure, stdlib-only metrics
  (`explained_fraction`, `formula_reachable_masses`, `sample_null`,
  `ceiling_with_ci`, `nitrogen_rule_parity`).
- `src/data_generation/phase0/run_ceiling.py` — corpus runner (the only part needing
  `mod`); writes the CSV + summary JSON.
- `src/data_generation/phase0/regen_subset.py` — regenerate a subset's forward DGs
  with the current ruleset (reads SMILES from existing dumps; forward-only).
- `run/analysis/phase0_ceiling.sh`, `run/data/regen_subset.sh` — container wrappers.
- `src/plot/plot_phase0_ceiling.py` — figures.

## Reading the gate

- **Ceiling high (well above 0, raw points above y=x):** the rule library can explain
  the spectra; proceed to Phase 1 (true-vs-decoy discrimination).
- **Ceiling low / near 0:** the rule library is the bottleneck. Inspect the OE/EE
  split and per-molecule rows to see which chemistry is missing before any modeling.
- **M+• rate low:** an ionization-model problem (e.g. stale dumps, or a missing M+•
  rule) — fix before trusting the ceiling.

## Out of scope (Phase 0.2)

Per-molecule MØD cost and the extrapolated full-enumeration budget → the crossover
N\* = B / cost_per_molecule that decides whether Phase 2's selective construction is
needed. A timed full regeneration doubles as this cost measurement.
