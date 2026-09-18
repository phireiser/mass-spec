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
"any heavy atom". That, rather than a wider or narrower shell, is the next
thing to test.
