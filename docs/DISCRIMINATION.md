# Discrimination — Phase-1 True-vs-Decoy Gate

The make-or-break gate for the EI spectrum-to-structure thesis. The whole system is
built to take an observed spectrum and pick the correct structure out of a pool of
same-formula candidates. Before training any forward model, this asks the prior
question: **at unit resolution, do the observed EI spectra of same-formula isomers
actually separate the true molecule from its decoys?** If real, measured spectra of
isomers are near-identical, then no structure→spectrum predictor can identify the
molecule from intensities — the ceiling on discrimination is a property of the data,
not the model. This gate needs **no new MØD compute**: it uses only the measured NIST
spectra already in the Parquet store.

## The metric — best-decoy cosine

A structure→spectrum predictor identifies the true molecule over a same-formula decoy
iff

```
cosine(observed_true, predicted_true) > cosine(observed_true, predicted_decoy)
```

Substitute each candidate's *real* NIST spectrum for the prediction (a perfect
predictor). The right-hand side becomes `cosine(observed_true, observed_decoy)`, so
the **highest cosine any same-formula decoy's real spectrum reaches against the query
is exactly the bar the forward model's predicted-true spectrum must clear** to win
that molecule. Its distribution across the corpus is the target the forward half of
Phase 1 has to hit.

Read the bar as an **oracle-decoy** bar: it assumes decoys are predicted *perfectly*.
Real decoy-prediction error only lowers the right-hand side, so the true forward model
generally has *more* slack than this number suggests — but it must also predict the
true spectrum well enough to stay above it.

## What it computes

Working at the frozen contract (integer m/z, `bin_width=1.0`, sqrt-intensity, L2,
dot-product cosine — identical to `machine_learning.data.bin_spectrum`):

For every target in `data/compounds.csv` that resolves to a spectrum in the store and
has ≥ 1 same-formula decoy (a different InChIKey with the same molecular formula
anywhere in the store):

- **best_decoy_cosine** — max cosine of the query against any same-formula decoy's real
  spectrum. The per-target discrimination bar.
- **margin** = `1 − best_decoy_cosine` — the oracle slack (self scores 1.0).
- **mean/median_decoy_cosine**, and counts of decoys above 0.7 / 0.8 / 0.9.
- **true_rank / identified** — rank of the true molecule among `{self} ∪ decoys` by
  the oracle library match. Always 1 unless a decoy's real spectrum ties the query
  exactly (a near-duplicate/stereoisomer entry) — a sanity check on the store, not a
  model result.
- **best_decoy_name** — the nearest confuser, for eyeballing (e.g. naphthalene's is
  azulene at 0.995; several are stereoisomer duplicates like serine / dl-Serine).

Plus a corpus-wide **cross-isomer** read independent of the target set: the cosine of
*every* same-formula pair in the store (groups capped at `--max-group` structures to
bound the O(n²) cost).

## How to run

```bash
bash run/analysis/discrimination.sh                     # all targets
bash run/analysis/discrimination.sh --names limonene,toluene   # smoke
```

Needs `pyarrow` + `rdkit` (no `mod`), so it runs inside `mol-spectro.sif`. Writes
`outputs/metrics/{discrimination_per_target.csv, discrimination_summary.json}`. Plot:

```bash
apptainer exec ... python src/plot/plot_discrimination.py   # -> outputs/plots/discrimination.png
```

The pure preprocessing/cosine lives in
`src/data_generation/analysis/discrimination/spectrum_ops.py` (stdlib only, so
`src/tests/unit_test_discrimination.py` runs bare and pins parity to the ML binning).

## Result (2026-07-03, current store: 19,670 spectra / 5,543 formulas)

**124 targets** have ≥ 1 same-formula decoy. Oracle library-match top-1 = 1.00 (no
exact spectral duplicates among decoys — sanity passes). The discrimination bar is
**hard**:

- **best_decoy_cosine: mean 0.82, median 0.88.** For half the targets a decoy's real
  spectrum already sits above 0.88 cosine to the true.
- **58 / 124 targets have a same-formula decoy above 0.9** (near-degenerate — some are
  stereoisomers EI cannot distinguish in principle).
- Corpus-wide, over **137,485 same-formula pairs**, the median cross-isomer cosine is
  **0.71** and **15%** exceed 0.9.

Caveat: the store groups by NIST's formula string, which mislabels isotopologues
(Methanol-D4 as "CH4O"). Their spectra are mass-shifted, so they rarely become the
*nearest* confuser and barely move `best_decoy_cosine`, but they do pad the decoy
counts and the all-pairs distribution slightly. The decoy *generation* set
(`build_decoy_set`) filters them out via RDKit.

**Interpretation / gate reading.** Unit-resolution EI intensity patterns leave a large
fraction of same-formula isomers spectrally close *even with perfect information*. The
forward model does not need to merely predict a plausible spectrum; on ~half the
corpus it must resolve a < 0.1-cosine margin between the true structure and its nearest
isomer. This does **not** fail the thesis — the margin is workable for the easy tail
(p25 margin 0.035, p75 0.23) and some near-1.0 decoys are genuine stereoisomer
duplicates that should be excluded — but it sets a demanding accuracy target and says
discrimination, not gross spectrum shape, is where the model earns its keep.

## Next (the expensive half of Phase 1) — the decoy generation batch

The forward-model half replaces `predicted_decoy` with an actual MØD forward
prediction per candidate structure — i.e. it needs a forward DG dump for every decoy
structure, then the same cosine ranking.

`build_decoy_set` collects the unique same-formula decoy structures for the target set
and writes ready-to-submit `name,smiles,category` CSVs (the format `data_gen.sh`
consumes), RDKit-deduplicated and isotopologue-filtered, sorted easy→hard by
heavy-atom count:

```bash
apptainer exec ... python -m src.data_generation.analysis.discrimination.build_decoy_set --out-dir data
# -> data/decoys.csv (full), data/decoys_wave1.csv (<=9 heavy), data/decoys_wave2.csv (>9)
```

Current set: **1,155 decoy structures need generation** (21 already have a dump),
across 116 targets — **490 in wave 1, 665 in wave 2**. ~45% are acyclic aliphatics
(the Phase-0 pathological class), so the batch inherits the heavy cost tail. Run it via
the `DEFINITION_FILE` override on `data_gen.sh` (see that script's header). Stage in two
waves and gate wave 2 on the sacct cost observed in wave 1 — that measurement also
re-answers the Phase-0 enumeration-cost question on the ~6×-faster `sub_group` code.

Then compute forward discrimination (MØD mass-set vs observed) and compare against this
oracle bar and against the NIST library match to localize failure (oracle-Generate
works but learned fails ⇒ sparse-teacher spectrum bias).
