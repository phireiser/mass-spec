"""
main file to execute

test call with e.g.
python src/mod_fragmentation/main.py --smiles C1=CC=CC=C1 --name benzene --output-dir data/processed/
"""

import argparse
from pathlib import Path
import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization, build_migration_rules
from src.data_generation.core import strategy
from src.project_paths import shared_path


parser = argparse.ArgumentParser(description="Using MØD as a MassSpec Fragmenter")
parser.add_argument("--smiles", type=str, required=True, help="SMILES String of Molecule")
parser.add_argument("--name", type=str, required=True, help="Molecule Name")
parser.add_argument("--output-dir", type=str, required=True, help="Directory for output files")
parser.add_argument("--spectra-folder", type=str, default=str(shared_path("PARQUET_DIR_REL")), help="Directory containing the NIST spectra Parquet store")
parser.add_argument("--number-threads", type=int, default=1, help="number of threads for mod (production runs 1 per SLURM cpus-per-task; direct runs default to 1 to match)")
parser.add_argument("--frag-repeat", type=int, default=5,
                    help="Max sequential fragmentation rounds (mod.repeat depth) for both passes. "
                         "Default 5 reproduces current output. Lowering it bounds the DG growth on "
                         "the molecules that OOM in forward, at the cost of dropping deep fragments; "
                         "~14%% of molecules still produce new fragments at rounds 4-5, so validate "
                         "peak coverage before lowering below 5.")
parser.add_argument("--no-migration", action="store_true",
                    help="Disable the fully delocalized charge model (charge/radical "
                         "migration rules). Reproduces the localized per-site scheme; "
                         "used for side-by-side baseline vs migration comparisons.")
parser.add_argument("--migration-tail-min-heavy", type=int, default=18, metavar="N",
                    help="Saturated-tail scoping, SIZE clause: a molecule is in the tail only if "
                         "it has >= N heavy atoms. N<=0 disables tail scoping entirely (full "
                         "migration for every molecule -- the configuration that TIMES OUT on "
                         "steroids). Size alone is not enough; see the reactive-fraction clause.")
parser.add_argument("--migration-tail-min-cyclomatic", type=int, default=2, metavar="C",
                    help="Saturated-tail scoping, STRUCTURE clause (OR'd with --migration-tail-"
                         "min-heavy): a molecule is structurally expensive if it has >= C "
                         "independent cycles (|E|-|V|+1). C<=0 disables the ring clause and "
                         "reverts to size-only. Size alone misses the saturated polycycles: at "
                         "10 heavy atoms and rf 0.000 alike, decane builds in 5.1 s and the "
                         "tricyclic CC1(C)C2CC3C1C3(C)C2 in 13 h16. 2 (not 1) because that is "
                         "where the cap stops being lossless -- monocyclic piperidine loses "
                         "26.5%% of its NIST intensity when capped, fused decalin/steroids "
                         "lose nothing.")
parser.add_argument("--migration-tail-max-reactive-fraction", type=float, default=0.66,
                    metavar="F",
                    help="Saturated-tail scoping, CHEMISTRY clause: a molecule is in the tail "
                         "only if its reactive_heavy_fraction < F (fraction of heavy atoms that "
                         "are hetero / on / adjacent-to unsaturation). Size alone misfires: "
                         "cholesterol(28 heavy) and riboflavin(27) are indistinguishable by "
                         "size, but rf is 0.250 vs 1.000 -- and migration's real wins (glucose, "
                         "sucrose) sit at rf 1.000. F=0.66 captures all 8 steroids: it was 0.6, "
                         "which split the steroid cluster and left estrone (exactly 13/20=0.650) "
                         "and aldosterone (0.654) on uncapped migration -- the only two failures "
                         "of the full rebuild. The test is >=, so 0.65 would NOT catch estrone; "
                         "the next tail-eligible molecule up is beta-carotene at 0.800. "
                         "F>1.0 disables the chemistry clause.")
parser.add_argument("--migration-tail-policy", type=str, default="cap",
                    choices=strategy.MIGRATION_TAIL_POLICIES,
                    help="What to do with molecules in the saturated tail. 'cap' (default): run "
                         "migration bounded to --migration-tail-cap charge/radical variants per "
                         "parent-mass skeleton. That makes the tail buildable at all -- "
                         "progesterone 67 min, cholesterol 88 min, versus a >9h timeout with NO "
                         "dump uncapped -- and is a strict SUPERSET of the no-migration result "
                         "(zero masses lost, +24 masses each, +5.2%%/+4.7%% of NIST intensity). "
                         "'off': skip migration for them; their TPR gain is not distinguishable "
                         "from chance (progesterone hit rate 0.810 vs 0.793 random, p=0.56) "
                         "because a steroid's NIST reference covers ~75%% of the candidate "
                         "masses, so this is the choice if you would rather not pay ~1.5h a "
                         "molecule for coverage of unproven value. 'gate': profit gate instead "
                         "(3h18/5h07, and lossier than the cap). 'full': unguarded migration "
                         "everywhere -- this is what times out on the tail (A/B use only). "
                         "Molecules OUTSIDE the tail always get full UNCAPPED migration "
                         "regardless: the cap is lossy there (piperidine loses 26.5%% of its NIST "
                         "intensity at cap 3) and there is deliberately no switch to apply it.")
parser.add_argument("--migration-tail-cap", type=int, default=strategy.DEFAULT_TAIL_CAP,
                    metavar="N",
                    help="Variants per parent-mass skeleton under --migration-tail-policy cap "
                         f"(default {strategy.DEFAULT_TAIL_CAP}). Cap 3 was measured to cost "
                         "1.20x the species, 1.69x the wall and 1.81x the isomorphism calls of "
                         "cap 2 for exactly one extra mass (progesterone m/z 86, +0.1%% of NIST "
                         "intensity), so raising it buys very little.")
parser.add_argument("--subgroup-diag", action="store_true", help="Enable subgroup diagnostics")
parser.add_argument("--mem-diag", type=str, default=None, metavar="CSV",
                    help="Localise the exploding derivation: log per-derivation peak-RSS growth "
                         "events (rule, reactant mass/charge, embedding fan-out) to this CSV. "
                         "Off by default; used to diagnose the forward OOMs.")
parser.add_argument("--avoid-reprocessing", action="store_true", help="Avoid reprocessing if output exists")
parser.add_argument("--skip-backward", action="store_true",
                    help="[deprecated] Force-skip the backward pass. The backward pass is now "
                         "skipped by default; this flag is kept so existing forward-only callers "
                         "keep working. Pass --run-backward to opt back in.")
parser.add_argument("--run-backward", action="store_true",
                    help="Opt in to building the backward (recombination) DG. Off by default: the "
                         "backward dump is not consumed by the ML pipeline and its generative build "
                         "is the dominant OOM/timeout source. --skip-backward overrides this.")
parser.add_argument("--name-by-cas", action="store_true",
                    help="Name the dump by the CAS registry number resolved from the store "
                         "(the project-wide single identifier) instead of --name; falls back "
                         "to --name if the molecule is not in the store")
args = parser.parse_args()

# Enable subgroup diagnostics
if args.subgroup_diag:
    utils.enable_subgroup_diag(True)

# Enable per-derivation memory instrumentation (localise the exploding derivation)
if args.mem_diag:
    utils.enable_mem_diag(args.mem_diag)

mod.getConfig()
mod.config.common.numThreads = args.number_threads
print(args.number_threads, "threads requested")
print(f"Using {mod.config.common.numThreads} threads")

# CAS is the single project-wide identifier used to name every dump.
dump_name = args.name
if args.name_by_cas:
    cas = utils.get_cas_by_smiles(args.smiles, Path(args.spectra_folder))
    if cas:
        dump_name = cas
    else:
        print(f"  --name-by-cas: no CAS in store for {args.name} ({args.smiles}); "
              f"falling back to --name '{args.name}'")

output_path_fwd = Path(args.output_dir) / "fwd/" / (dump_name + ".dmp")
output_path_bwd = Path(args.output_dir) / "bwd/" / (dump_name + ".dmp")

molecule = utils.graph_from_smiles(args.smiles, dump_name)
molecule_term= utils.term_from_graph(molecule)

aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

ls = mod.LabelSettings(
    mod.LabelType.Term,
    mod.LabelRelation.Specialisation
)

# ------------------------------------------------------------ #
print("\nmol spectrum of", molecule.name)
print("\nforward\n")

ionization_term_fwd = [
    utils.term_from_rule(r)
    for r in utils.apply_constraints(ionization, aoc)
]
fragmentation_term_fwd = [
    utils.term_from_rule(r)
    for r in utils.apply_constraints(fragmentation, aoc)
]
# Migration rules are authored directly in term mode (independent element/radical/bond
# variables the DFS->term_from_rule path cannot express), so they skip apply_constraints
# and term_from_rule. Restrict the migrating-onto atom to this molecule's occurring heavy
# atoms so charge/radical never lands on hydrogen.
heavy_atoms = sorted(aoc - {"H"})

# Per-molecule migration scoping. Migration is ON by default -- it is additive (never removes
# a peak) and its chance-corrected wins are large and real (glucose NIST TPR 0.096->0.413,
# p=3.7e-05; limonene 0.356->0.624, p=3.3e-04; sucrose 0.068->0.270, p=0.005) -- but it costs
# ~25x net compute, scaling as roughly blowup ~ 0.5 * heavy^1.4, so it must be switched off for
# the saturated tail where that cost is unbounded and the benefit is a metric artifact.
# `strategy.migration_scope` owns that decision and documents the evidence; it returns the
# reason string so each run records why it did what it did.
heavy_count = sum(
    1 for v in molecule_term.vertices
    if utils.parse_term_atom(v.stringLabel)[0] != "H"
)
reactive_fraction = utils.reactive_heavy_fraction(molecule_term)
cyclomatic = utils.cyclomatic_number(molecule_term)
scope = strategy.migration_scope(
    heavy_count=heavy_count,
    reactive_fraction=reactive_fraction,
    cyclomatic=cyclomatic,
    min_heavy=args.migration_tail_min_heavy,
    min_cyclomatic=args.migration_tail_min_cyclomatic,
    max_reactive_fraction=args.migration_tail_max_reactive_fraction,
    policy=args.migration_tail_policy,
    tail_cap=args.migration_tail_cap,
)
if args.no_migration:
    scope = strategy.MigrationScope(False, False, None, "migration disabled (--no-migration)")
use_migration, gate_migration, migration_cap, scope_reason = scope

# Migration rules are authored directly in term mode (independent element/radical/bond
# variables the DFS->term_from_rule path cannot express), so they skip apply_constraints
# and term_from_rule. Restrict the migrating-onto atom to this molecule's occurring heavy
# atoms so charge/radical never lands on hydrogen.
migration_term_fwd = build_migration_rules(heavy_atoms) if use_migration else []
print(f"migration: {scope_reason}")
if use_migration:
    print(f"  {len(migration_term_fwd)} rule(s) over heavy atoms {heavy_atoms}"
          f"{'; profit gate ACTIVE' if gate_migration else ''}"
          f"{f'; multiplicity cap {migration_cap}/parent-mass skeleton' if migration_cap else ''}")

ionization_term_bwd=[r.makeInverse() for r in ionization_term_fwd]
fragmentation_term_bwd=[r.makeInverse() for r in fragmentation_term_fwd]

dg_fwd = mod.DG(
    graphDatabase = [molecule_term],
    labelSettings = ls
)

strat_fwd = strategy.make_fwd_strategy(
    derivation_graph=dg_fwd,
    universe=molecule_term,
    ionization=ionization_term_fwd,
    fragmentation=fragmentation_term_fwd,
    migration=migration_term_fwd,
    gate_migration=gate_migration,
    migration_cap=migration_cap,
    max_mass=molecule.exactMass,
    frag_repeat=args.frag_repeat,
)

fwd_dir = Path(args.output_dir) / "fwd/"
dg_fwd_reused = False
if args.avoid_reprocessing and utils.dump_is_complete(molecule.name, fwd_dir):
    # Marker says the dump is complete; the load doubles as the integrity check.
    try:
        dg_fwd = utils.load_derivation_graph(name=molecule.name, path=fwd_dir)
        dg_fwd_reused = True
        print(f"  Forward dump {output_path_fwd} complete and loadable, skipping...")
    except Exception as e:
        print(f"  Forward dump {output_path_fwd} present but not loadable ({e}); rebuilding...")

if not dg_fwd_reused:
    dg_fwd.build().execute(strat_fwd)

    utils.dump_derivation_graph(
        dg=dg_fwd,
        rule_list=ionization_term_fwd + migration_term_fwd + fragmentation_term_fwd,
        name=molecule.name,
        smiles=args.smiles,
        path=fwd_dir
    )

# ------------------------------------------------------------ #
# Backward pass is opt-in: skip unless --run-backward is given (and --skip-backward
# always wins for the existing forward-only callers). The backward recombination DG
# is unused downstream and is the dominant OOM/timeout source, so forward-only is the
# default. See the ML loader, which now treats a missing bwd dump as an empty backward
# collection rather than dropping the molecule.
run_backward = args.run_backward and not args.skip_backward
if not run_backward:
    reason = "--skip-backward" if args.skip_backward else "default; pass --run-backward to enable"
    print(f"\nskipping backward pass ({reason})\n")
    raise SystemExit(0)

print("\nbackward\n")

spectra_jdx = utils.get_spectra_by_smiles(args.smiles, Path(args.spectra_folder))
spectra_jdx = [x[0] for x in spectra_jdx]
# Keep the fragments whose nominal mass matches an observed peak. Use the
# term-space mass helper: it returns None for non-molecule fragments -- those
# with an atom mod won't assign a mass to (placeholder ``_A`` atoms, or
# aromatic-typed atoms such as a lone ``c`` that mod perceives on some generated
# cations) -- which have no defined mass and cannot match a peak. This avoids the
# ``LogicError: Can not get exact mass of a non-molecule`` that
# ``graph_from_term(frag).exactMass`` raises on them. The forward graphDatabase
# legitimately contains such non-molecule graphs (see the ``isMolecule`` guard in
# ``utils.spect_mol``), so they must be skipped, not left to abort the whole
# backward pass. The helper also drops the GML round-trip.
frags_in_spectra = [
    frag for frag in dg_fwd.graphDatabase
    if (mass := utils.exact_mass_from_term(frag)) is not None
    and int(mass) in spectra_jdx
]

# filter fragments out ancerters of other fragments
bwd_universe = utils.filter_ancestors_out(frags_in_spectra, dg_fwd)

dg_bwd = mod.DG(
    graphDatabase=dg_fwd.graphDatabase,
    labelSettings=ls
)

strat_bwd = strategy.make_bwd_strategy(
    derivation_graph=dg_bwd,
    universe=bwd_universe,
    fragmentation=fragmentation_term_bwd,
    max_mass=molecule.exactMass,
    frag_repeat=args.frag_repeat,
)

bwd_dir = Path(args.output_dir) / "bwd/"
if args.avoid_reprocessing and utils.dump_is_complete(molecule.name, bwd_dir) \
        and utils.dump_is_loadable(molecule.name, bwd_dir):
    print(f"Backward dump {output_path_bwd} complete and loadable, skipping...")
else:
    dg_bwd.build().execute(strat_bwd)

    utils.dump_derivation_graph(
        dg=dg_bwd,
        rule_list=ionization_term_bwd + fragmentation_term_bwd,
        name=molecule.name,
        smiles=args.smiles,
        path=bwd_dir
    )

print("\n\n")
