"""
load analyse a derivation graph
"""
import ctypes
import sys
import os
import argparse
import pandas as pd
from pprint import pprint

sys.setdlopenflags(sys.getdlopenflags() | ctypes.RTLD_GLOBAL)
sys.path.append("/home/talax/xtof/local/Mod/lib64/")
sys.path.append(
    "/home/mescalin/reiserp/Nextcloud/"
    "studium/computationalScience/thesis/mol/fragmentation/"
    )
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import utils
from rules import fragmentation, ionization
import strategy
import mod


#parser = argparse.ArgumentParser(description="Using MØD as a MassSpec Fragmenter")
#parser.add_argument("--smiles", type=str, required=True, help="SMILES String of Molecule")
#parser.add_argument("--name", type=str, required=True, help="Molecule Name")
#args = parser.parse_args()


#molecule = mod.smiles(args.smiles, args.name)
smiles = "O=C(O)C(N)CC=1C=CC=CC1"
name = "phenylalanine"

smiles = "C[C@@H](C(=O)O)N"
name = "alanine"


molecule = mod.smiles(smiles, name)
molecule_term = utils.term_from_graph(molecule)

aoc = utils.all_occuring([molecule], utils.allAtoms)

ionization_term = [map(utils.term_from_rule, utils.apply_constraints(ionization, aoc))]
fragmentation_term = [map(utils.term_from_rule, utils.apply_constraints(fragmentation, aoc))]

dg, rule_list  =  utils.load_derivation_graph(
    molecule.name,
    path="/home/mescalin/reiserp/Nextcloud/"
    "studium/computationalScience/thesis/mol/dump/"
    )

dg.print()

#utils.print_rules(ionization_term + fragmentation_term)

with pd.option_context(
    'display.max_rows', None, 'display.max_columns', None,
    'display.width', None, 'display.max_colwidth', None
    ):
    print(utils.rule_usage(dg, molecule_term, mod.inputRules).query("active == True"))

print("\n\n")
print("spectrum coverage")
pprint(utils.spectrum_statistic(dg, molecule_term), width=120)
