"""
main file to execute on slurm
"""

import argparse
import mod

from mass_spec_modeling.mod_fragmentation import utils
from mass_spec_modeling.mod_fragmentation.rules import fragmentation, ionization
from mass_spec_modeling.mod_fragmentation import strategy


parser = argparse.ArgumentParser(description="Using MØD as a MassSpec Fragmenter")
parser.add_argument("--smiles", type=str, required=True, help="SMILES String of Molecule")
parser.add_argument("--name", type=str, required=True, help="Molecule Name")
parser.add_argument("--output-dir", type=str, required=True, help="Directory for output files")
parser.add_argument("--number-threads", type=int, default=64, help="number of threads for mod")
args = parser.parse_args()

mod.getConfig()
mod.config.common.numThreads= args.number_threads

molecule = mod.smiles(args.smiles, args.name)
molecule_term= utils.term_from_graph(molecule)

aoc = utils.all_occuring([molecule], utils.allAtoms)

ls = mod.LabelSettings(
    mod.LabelType.Term,
    mod.LabelRelation.Unification
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

dg_fwd.build().execute(strat_fwd)

utils.dump_derivation_graph(
    dg=dg_fwd,
    rule_list=ionization_term_fwd + fragmentation_term_fwd,
    name=molecule.name,
    smiles=args.smiles,
    true_spectrum=utils.get_spectra_from_pubchem(args.smiles),
    path=args.output_dir + "/fwd/"
)

# ------------------------------------------------------------ #
print("\nbackward\n")

spectra_jdx = utils.get_spectra_from_local_jdx(molecule.name)
spectra_jdx = [x[0] for x in spectra_jdx]
frags_in_spectra = [frag for frag in dg_fwd.createdGraphs \
    if int(utils.graph_from_term(frag).exactMass) in spectra_jdx]

# filter fragments out ancerters of other fragments
bwd_universe = utils.filter_ancestors_out(frags_in_spectra, dg_fwd)

ionization_term_bwd=[r.makeInverse() for r in fragmentation_term_fwd]
fragmentation_term_bwd=[r.makeInverse() for r in fragmentation_term_fwd]

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

dg_bwd.build().execute(strat_bwd)

utils.dump_derivation_graph(
    dg=dg_bwd,
    rule_list=ionization_term_bwd + fragmentation_term_bwd,
    name=molecule.name,
    smiles=args.smiles,
    true_spectrum=utils.get_spectra_from_pubchem(args.smiles),
    path=args.output_dir + "/bwd/"
)

print("\n\n")
