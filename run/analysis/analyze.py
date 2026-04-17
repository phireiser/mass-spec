"""
load analyse a derivation graph
"""
from pprint import pprint
import subprocess
import argparse
import pandas as pd
import mod

from mass_spec_modeling.mod_fragmentation import utils
from mass_spec_modeling.mod_fragmentation.rules import fragmentation, ionization


parser = argparse.ArgumentParser(description="Analyzer of MØD dumps generated with MassSpec rules")
parser.add_argument("--smiles", type=str, required=True, help="SMILES String of Molecule")
parser.add_argument("--name", type=str, required=True, help="Molecule Name")
parser.add_argument("--dir", type=str, required=True, help="Directory of loading files")
args = parser.parse_args()

molecule = mod.Graph.fromSMILES(args.smiles, args.name)
molecule_term = utils.term_from_graph(molecule)

aoc = utils.all_occuring([molecule], utils.allAtoms)

ionization_term = [utils.term_from_rule(rule) \
    for rule in utils.apply_constraints(ionization, aoc)]
fragmentation_term = [utils.term_from_rule(rule) \
    for rule in utils.apply_constraints(fragmentation, aoc)]


dg, rule_list =  utils.load_derivation_graph(
    molecule.name,
    path="/home/mescalin/reiserp/Nextcloud/"
    "studium/computationalScience/thesis/mol/dump/fwd/"
    )

print("\n")
print("dump loaded")
print("\n\n")

dg.print()
utils.print_rules(ionization + fragmentation)


with pd.option_context(
    'display.max_rows', None, 'display.max_columns', None,
    'display.width', None, 'display.max_colwidth', None
    ):
    print(utils.rule_usage(dg, molecule_term, mod.inputRules).query("active == True"))

print("\n\n")
print("spectrum coverage")
pprint(utils.spectrum_statistic(dg, molecule_term), width=120)


print("\n\n")
print("mod post running ...")
mod.post.flushCommands()

process = subprocess.run(
   ["stdbuf", "-oL", "-eL", "/home/talax/xtof/local/Mod/bin/mod_post"],
    check=False,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=1
)
