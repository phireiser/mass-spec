"""
load analyse a derivation graph
"""
from pprint import pprint
import subprocess
import argparse
import sys
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
parser.add_argument("--spectra-folder", type=str, default=str(shared_path("PARQUET_DIR_REL")),
                    help="NIST Parquet store, used to resolve --name to its CAS")
args = parser.parse_args()

molecule = utils.graph_from_smiles(args.smiles, args.name)
molecule_term = utils.term_from_graph(molecule)

aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

ionization_term = [utils.term_from_rule(rule) \
    for rule in utils.apply_constraints(ionization, aoc)]
fragmentation_term = [utils.term_from_rule(rule) \
    for rule in utils.apply_constraints(fragmentation, aoc)]


# Dumps are named by CAS (`main.py --name-by-cas`); pre-rename dumps still carry
# the human name, so resolve rather than assume either one.
stem = utils.resolve_dump_stem(args.name, args.smiles, args.dir, args.spectra_folder)
if stem is None:
    tried = utils.dump_stem_candidates(
        args.name, utils.get_cas_by_smiles(args.smiles, args.spectra_folder))
    sys.exit(f"no dump for {args.name!r} in {args.dir} (tried stems: {', '.join(tried)})")
if stem != args.name:
    print(f"resolved {args.name!r} -> CAS {stem}")

dg = utils.load_derivation_graph(
    stem,
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
    # Pass the ORIGINAL --smiles: the reference lookup canonicalises SMILES -> InChIKey ->
    # CAS, and the term round-trip drops stereochemistry, which silently yields zero
    # reference peaks for stereo-dependent molecules (sugars).
    print(describe.rule_usage(dg, molecule_term, mod.inputRules, smiles=args.smiles)
          .query("active == True"))

print("\n\n")
print("spectrum coverage")
pprint(describe.spectrum_statistic(dg, molecule_term, smiles=args.smiles), width=120)


print("\n\n")
print("mod post running ...")
mod.post.enableCompileSummary()
mod.post.flushCommands()

subprocess.run(["mod_post"], check=True)
