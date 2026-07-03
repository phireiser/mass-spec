# Feasibility — MØD Explainability Ceiling & Enumeration Cost

The cheap, no-ML gate for the EI spectrum-to-structure thesis. Before building any
learned model or scaling teacher-DAG construction, it answers two questions:
**(1) does the MØD rule library actually explain the high-intensity peaks in real EI
spectra?** (the explainability *ceiling*), and **(2) is full forward enumeration
affordable across the corpus?** (the per-molecule *cost* and the budget crossover
`N* = B / cost_per_molecule`). If the ceiling is low, the rule library — not the
model — is the bottleneck. If the cost tail is intractable, selective construction
is required before scaling. Both must be settled before modeling.

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
# array regen -> outputs/regen_subset/fwd
# dependent ceiling -> outputs/metrics/{ceiling_per_molecule.csv,ceiling_summary.json}
```

Each task is wrapped in `/usr/bin/time -v`, so the per-task logs under
`outputs/logs/regen_subset/slurm/` double as per-molecule cost data (fed to
`cost_analysis.py`; see the cost section below).

Full corpus (all ~150 molecules that have both a dump and a spectrum):

```bash
sbatch run/hpc/regen_subset.sh --all-with-spectrum
```

> **Cost warning.** Per-molecule cost is dominated by *saturated aliphatic* content,
> not size, and spans ~6000× on the subset (butane C4H10 ~4 h; aromatics seconds).
> The full corpus contains longer saturated chains (pentane … nonane, alkyl acids),
> so expect a heavy tail — keep the wall-time cap generous and treat the result as
> the cost distribution (use it for N\* = B / cost, not a mean).

Ceiling on an existing set of (fresh) dumps:

```bash
bash run/analysis/ceiling.sh                       # full corpus, default dirs
bash run/analysis/ceiling.sh --names acetone,toluene,aniline --draws 200   # quick
```

Cost / budget analysis from the array's sacct record + logs (stdlib, runs bare):

```bash
sacct -j <array_job_id> --format=JobID,State,ElapsedRaw,MaxRSS,ReqMem -P -n > sacct.txt
python3 src/data_generation/utils/analysis/feasibility/cost_analysis.py \
  --sacct-file sacct.txt \
  --manifest outputs/regen_subset/manifest.tsv \
  --log-dir outputs/logs/regen_subset/slurm/<array_job_id> \
  --out-dir outputs/metrics
# -> outputs/metrics/{cost_per_molecule.csv,cost_summary.json}
```

Plots (matplotlib lives in the container; both default to `outputs/plots/`):

```bash
python src/plot/plot_ceiling.py   # -> outputs/plots/ceiling.png
python src/plot/plot_cost.py      # -> outputs/plots/cost.png
```

Unit tests for the pure metrics (run bare, no container):

```bash
python3 src/tests/unit_test_ceiling.py
```

## Code

- `src/data_generation/utils/analysis/feasibility/ceiling_metrics.py` — pure, stdlib-only metrics
  (`explained_fraction`, `formula_reachable_masses`, `sample_null`,
  `ceiling_with_ci`, `nitrogen_rule_parity`).
- `src/data_generation/utils/analysis/feasibility/run_ceiling.py` — corpus runner (the only part
  needing `mod`); writes the ceiling CSV + summary JSON to `outputs/metrics`.
- `src/data_generation/utils/analysis/feasibility/cost_analysis.py` — pure, stdlib-only cost / N\*
  analysis from a sacct dump + array logs; writes the cost CSV + summary JSON.
- `src/data_generation/utils/analysis/feasibility/regen_subset.py` — regenerate a subset's forward
  DGs with the current ruleset (reads SMILES from existing dumps; forward-only).
- `run/analysis/ceiling.sh`, `run/hpc/regen_subset.sh` — container / SLURM wrappers.
- `src/plot/plot_ceiling.py`, `src/plot/plot_cost.py` — figures (→ `outputs/plots`).

## Reading the gate

- **Ceiling high (well above 0, raw points above y=x):** the rule library can explain
  the spectra; proceed to Phase 1 (true-vs-decoy discrimination).
- **Ceiling low / near 0:** the rule library is the bottleneck. Inspect the OE/EE
  split and per-molecule rows to see which chemistry is missing before any modeling.
- **M+• rate low:** an ionization-model problem (e.g. stale dumps, or a missing M+•
  rule) — fix before trusting the ceiling.

## Reading the cost gate

`cost_analysis.py` reports per-molecule wall time (the only honest cost unit — the
`time -v` figures in the logs wrap `srun`, so their CPU/RSS is the launcher, not the
payload; use sacct's `.0`-step MaxRSS for memory). Output graph count does **not**
predict cost, so it can't be used to pre-filter cheap molecules.

- **Cost light-tailed, no censoring:** full enumeration is affordable; N\* comfortably
  exceeds the projected corpus → skip selective construction.
- **Heavy tail / tasks censored at the wall:** a hard subset (saturated aliphatics,
  large flexible molecules) is individually intractable *regardless of corpus N* → full
  enumeration is not viable; selective / RL construction is required. This is a stronger
  condition than "corpus > N\*". TIMEOUT tasks are right-censored, so the reported mean
  is a lower bound and every N\* is an upper bound.
