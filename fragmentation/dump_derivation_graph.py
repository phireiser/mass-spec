"""
main file to execute on slurm
"""
import ctypes
import sys
import os
import argparse
sys.setdlopenflags(sys.getdlopenflags() | ctypes.RTLD_GLOBAL)
sys.path.append("/home/talax/xtof/local/Mod/lib64/")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import utils
from rules import fragmentation, ionization
import strategy
import mod

parser = argparse.ArgumentParser(description="Using MØD as a MassSpec Fragmenter")
parser.add_argument("--smiles", type=str, required=True, help="SMILES String of Molecule")
parser.add_argument("--name", type=str, required=True, help="Molecule Name")
args = parser.parse_args()

molecule = mod.smiles(args.smiles, args.name)
molecule_term = utils.termFromGraph(molecule)

aoc = utils.allOccuring([molecule], utils.allAtoms)

ionization_term = list(map(utils.termFromRule, utils.apply_constraints(ionization, aoc)))
fragmentation_term = list(map(utils.termFromRule, utils.apply_constraints(fragmentation, aoc)))

print("mol spectrum of", molecule.name)

# switch to term rewrite
ls = mod.LabelSettings(
    mod.LabelType.Term,
    mod.LabelRelation.Unification
    )

dg = mod.DG(
    graphDatabase = [molecule_term],
    labelSettings = ls
    )

strat = strategy.make_strategy(
    derivation_graph=dg,
    universe=molecule_term,
    ionization=ionization_term,
    fragmentation=fragmentation_term
    )

dg.build().execute(strat)

dg.dump(f"./dump/{molecule.name}")
