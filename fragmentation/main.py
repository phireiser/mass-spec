import pandas as pd
from pprint import pprint
import sys
import argparse

#include("tests/benzylAllyl_unified.py")
include("commons.py")
include("mols.py") # mols before rules
include("rules.py")
include("strategy.py")


parser = argparse.ArgumentParser(description="Philipp's Fragmenter")
parser.add_argument("filename", help="Input file name")
parser.add_argument("--smiles", type=str, required=True, help="SMILES String of Molecule")
parser.add_argument("--name", type=str, required=True, help="Moelcuel Name")

args = parser.parse_args()

molecule = smiles(args.smiles, args.name)

print("mol spectrum of", molecule.name)

strategy = makeStrategy(
    universe=[molecule],
    ionization=ionization_term,
    fragmentation=fragmentation_term
    )
ls = LabelSettings(
    LabelType.Term,
    LabelRelation.Unification
    ) # switch to term rewrite

dg = DG(graphDatabase=[molecule], labelSettings=ls)
dg.build().execute(strategy)

dg.dump(f"out/dump/{molecule.name}")



#with pd.option_context(
#    'display.max_rows', None,
#    'display.max_columns', None,
#    'display.width', None,
#    'display.max_colwidth', None
#    ):
#    print(rules_df)




#print_grammar(in_graphs = [toluene] #common_ei_molecules
#, in_rules = ionization + fragmentation)
#
#dg.print()
#
#print_rules(ionization_term + fragmentation_term)
