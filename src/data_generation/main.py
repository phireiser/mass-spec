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
parser.add_argument("--spectra-folder", type=str, default=str(shared_path("NIST_SPECTRA_DIR_REL")), help="Directory containing NIST .jdx spectra")
parser.add_argument("--number-threads", type=int, default=64, help="number of threads for mod")
parser.add_argument("--subgroup-diag", action="store_true", help="Enable subgroup diagnostics")
parser.add_argument("--avoid-reprocessing", action="store_true", help="Avoid reprocessing if output exists")
parser.add_argument("--skip-backward", action="store_true", help="Only build the forward DG (skip the backward pass)")
args = parser.parse_args()

# Enable subgroup diagnostics
if args.subgroup_diag:
    utils.enable_subgroup_diag(True)

mod.getConfig()
mod.config.common.numThreads = args.number_threads
print(args.number_threads, "threads requested")
print(f"Using {mod.config.common.numThreads} threads")

output_path_fwd = Path(args.output_dir) / "fwd/" / (args.name + ".dmp")
output_path_bwd = Path(args.output_dir) / "bwd/" / (args.name + ".dmp")

molecule = mod.Graph.fromSMILES(args.smiles, args.name)
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
    max_mass=molecule.exactMass
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
if args.skip_backward:
    print("\nskipping backward pass (--skip-backward)\n")
    raise SystemExit(0)

print("\nbackward\n")

spectra_jdx = utils.get_spectra_from_local_jdx(molecule.name, folder=Path(args.spectra_folder))
spectra_jdx = [x[0] for x in spectra_jdx]
frags_in_spectra = [frag for frag in dg_fwd.graphDatabase \
    if int(utils.graph_from_term(frag).exactMass) in spectra_jdx]

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
    max_mass=molecule.exactMass
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
