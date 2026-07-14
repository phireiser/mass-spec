"""
main file to execute

test call with e.g.
python src/mod_fragmentation/main.py --smiles C1=CC=CC=C1 --name benzene --output-dir data/processed/
"""

import argparse
from pathlib import Path
import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization
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
parser.add_argument("--subgroup-diag", action="store_true", help="Enable subgroup diagnostics")
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
        rule_list=ionization_term_fwd + fragmentation_term_fwd,
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
