#!/usr/bin/env python3
"""Re-measure the data-generation strategy bisection behind ``docs/DATA_GEN_PERFORMANCE.md``.

One configuration per invocation, printing a JSON line. Run it once per config from a
shell loop so each measurement gets a fresh interpreter: MØD keeps a process-global graph
database, and reusing a process lets a later config reuse canonical forms an earlier one
paid for, which quietly flatters whichever config runs last.

    for c in ionization frag1_unfiltered frag1_bounds frag1_subgroup full; do
        apptainer exec ... python /app/src/plot/bench_datagen_strategy.py --config $c
    done

The DG is built exactly as ``main.py`` builds it, through ``strategy.make_fwd_strategy``
where the config allows, so the numbers describe the shipping pipeline rather than a
re-implementation of it.
"""
import argparse
import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization, build_migration_rules
from src.data_generation.core import strategy
from src.data_generation.core.predicates import sub_group, charge_bound, amu_bound

CONFIGS = (
    "ionization",         # ionization only
    "frag1_unfiltered",   # + 1 fragmentation round, no filters at all
    "frag1_bounds",       # + 1 round, mass/charge bounds only (no sub_group)
    "frag1_subgroup",     # + 1 round, sub_group only (no bounds)
    "full",               # the shipping strategy
    # The two below drop ONE filter from the shipping strategy at full repeat depth. The
    # single-round rows above stopped discriminating once the predicate got cheap: at one
    # round nothing is rejected yet, so every filter combination returns the same subset.
    "full_no_subgroup",   # shipping strategy minus sub_group
    "full_no_bounds",     # shipping strategy minus charge_bound/amu_bound
)


def _staged(dg, rules, frag, frag_repeat, wrap_subgroup):
    """Reproduce make_fwd_strategy's terminal-round trim, optionally without sub_group."""
    if frag_repeat > 1:
        a, b = mod.repeat[frag_repeat - 1](rules), mod.repeat[1](list(frag))
        return (sub_group(a, dg) >> sub_group(b, dg)) if wrap_subgroup else (a >> b)
    a = mod.repeat[frag_repeat](rules)
    return sub_group(a, dg) if wrap_subgroup else a


def build(cfg, smiles, name, threads, frag_repeat, migration):
    mod.getConfig()
    mod.config.common.numThreads = threads

    molecule = utils.graph_from_smiles(smiles, name)
    molecule_term = utils.term_from_graph(molecule)
    aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

    ion = [utils.term_from_rule(r) for r in utils.apply_constraints(ionization, aoc)]
    frag = [utils.term_from_rule(r) for r in utils.apply_constraints(fragmentation, aoc)]
    mig = build_migration_rules(sorted(aoc - {"H"})) if migration else None

    ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
    dg = mod.DG(graphDatabase=[molecule_term], labelSettings=ls)

    if cfg == "full":
        strat = strategy.make_fwd_strategy(
            derivation_graph=dg, universe=molecule_term,
            ionization=ion, fragmentation=frag, migration=mig,
            max_mass=molecule.exactMass, frag_repeat=frag_repeat)
    else:
        rules = list(frag) + list(mig) if mig else list(frag)
        head = mod.addSubset(molecule_term) >> sub_group(mod.repeat[1](ion), dg)
        if cfg == "ionization":
            strat = head
        elif cfg == "frag1_unfiltered":
            strat = head >> mod.repeat[1](rules)
        elif cfg == "frag1_bounds":
            strat = head >> charge_bound(amu_bound(
                mod.repeat[1](rules), minimum=10, maximum=molecule.exactMass))
        elif cfg == "frag1_subgroup":
            strat = head >> sub_group(mod.repeat[1](rules), dg)
        elif cfg == "full_no_subgroup":
            strat = head >> charge_bound(amu_bound(
                _staged(dg, rules, frag, frag_repeat, wrap_subgroup=False),
                minimum=10, maximum=molecule.exactMass))
        elif cfg == "full_no_bounds":
            strat = head >> _staged(dg, rules, frag, frag_repeat, wrap_subgroup=True)
        else:
            raise SystemExit(f"unknown config {cfg!r}")
    return dg, strat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, choices=CONFIGS)
    ap.add_argument("--smiles", default="CC(=O)C")
    ap.add_argument("--name", default="acetone")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--frag-repeat", type=int, default=5)
    ap.add_argument("--no-migration", action="store_true")
    ap.add_argument("--unbounded-right", action="store_true",
                    help="Let DGVertexMapper enumerate right-side comatches "
                         "unbounded instead of right_limit=1.")
    args = ap.parse_args()

    if args.unbounded_right:
        _orig = utils.get_rule_2_molecule_maps

        def _unbounded(*a, **kw):
            kw["right_limit"] = None
            return _orig(*a, **kw)

        utils.get_rule_2_molecule_maps = _unbounded

    buf = io.StringIO()
    with redirect_stdout(buf):                     # MØD's round chatter is not the result
        dg, strat = build(args.config, args.smiles, args.name, args.threads,
                          args.frag_repeat, not args.no_migration)
        t0 = time.time()
        dg.build().execute(strat)
        wall = time.time() - t0
        species = sum(1 for _ in dg.vertices)
        edges = sum(1 for _ in dg.edges)

    print(json.dumps({
        "config": args.config, "molecule": args.name, "threads": args.threads,
        "frag_repeat": args.frag_repeat, "migration": not args.no_migration,
        "right": "unbounded" if args.unbounded_right else "limit1",
        "wall_s": round(wall, 2), "species": species, "derivations": edges,
    }))


if __name__ == "__main__":
    main()
