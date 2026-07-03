"""
load analyse a derivation graph
"""
from pprint import pprint
import subprocess
import argparse
import pandas as pd
import mod

from src.data_generation import utils
from src.data_generation.analysis import describe, printing
from src.data_generation.rules import fragmentation, ionization
from src.project_paths import shared_path



parser = argparse.ArgumentParser(description="Analyzer of MØD dumps generated with MassSpec rules")
parser.add_argument("--smiles", type=str, required=True, help="SMILES String of Molecule")
parser.add_argument("--name", type=str, required=True, help="Molecule Name")
parser.add_argument("--dir", type=str, required=True, help="Directory of loading files")
args = parser.parse_args()

molecule = mod.Graph.fromSMILES(args.smiles, args.name)
molecule_term = utils.term_from_graph(molecule)

aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

ionization_term = [utils.term_from_rule(rule) \
    for rule in utils.apply_constraints(ionization, aoc)]
fragmentation_term = [utils.term_from_rule(rule) \
    for rule in utils.apply_constraints(fragmentation, aoc)]


dg = utils.load_derivation_graph(
    molecule.name,
    path=args.dir,
    )

print("\n")
print("dump loaded")
print("\n\n")

dg.print()
printing.print_grammar([molecule], ionization + fragmentation)


with pd.option_context(
    'display.max_rows', None,
    'display.max_columns', None,
    'display.width', None,
    'display.max_colwidth', None
    ):
    print(describe.rule_usage(dg, molecule_term, mod.inputRules).query("active == True"))

print("\n\n")
print("spectrum coverage")
pprint(describe.spectrum_statistic(dg, molecule_term), width=120)


print("\n\n")
print("mod post running ...")
mod.post.enableCompileSummary()
mod.post.flushCommands()

subprocess.run(["mod_post"], check=True)
