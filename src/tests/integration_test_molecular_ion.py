"""
Integration test / sanity check for the shared EI molecular-ion rule
(rules.ei_molecular_ion, `[C] >> [C+.]`).

Confirms, across a range of organic molecules, that:
  1. the intact molecular ion M+. is generated (a charged species whose mass
     equals the neutral molecule's mass), and
  2. enabling the rule does not blow up the derivation graph (species count
     stays under a generous bound).

Like the toluene test this drives the real MOD engine, so it is slow and skipped
unless RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh).

SMILES are written in Kekulé form (explicit single/double bonds): term_from_graph
has no term encoding for aromatic bonds, so the aromatic SMILES form would fail
term parsing before the pipeline even starts.
"""

import os
import unittest

import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization
from src.data_generation.core import strategy


# (name, Kekulé SMILES): an aromatic, a substituted aromatic, a carbonyl
# (heteroatom) and a saturated alkane, so the carbon-localized molecular-ion rule
# is exercised on unsaturated, aromatic, heteroatom and fully saturated skeletons.
MOLECULES = [
    ("benzene", "C1=CC=CC=C1"),
    ("toluene", "CC1=CC=CC=C1"),
    ("acetone", "CC(=O)C"),
    ("butane", "CCCC"),
]

# Blow-up guard: toluene produces ~50 species; anything near this bound means the
# molecular-ion rule (or a downstream rule) is generating far more than expected.
MAX_SPECIES = 500


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh)",
)
class TestMolecularIon(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        mod.config.common.numThreads = 1

    def _run_pipeline(self, name, smiles):
        """Run ionization + fragmentation and return (exact_mass, n_species,
        n_charged, molecular_ion_present)."""
        molecule = mod.Graph.fromSMILES(smiles, name)
        molecule_term = utils.term_from_graph(molecule)
        aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

        ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
        dg = mod.DG(graphDatabase=[molecule_term], labelSettings=ls)

        ionization_terms = [utils.term_from_rule(r) for r in utils.apply_constraints(ionization, aoc)]
        fragmentation_terms = [utils.term_from_rule(r) for r in utils.apply_constraints(fragmentation, aoc)]

        strat = strategy.make_fwd_strategy(
            derivation_graph=dg,
            universe=molecule_term,
            ionization=ionization_terms,
            fragmentation=fragmentation_terms,
            max_mass=molecule.exactMass,
        )
        dg.build().execute(strat)

        target_mass = round(molecule.exactMass)
        n_species = 0
        n_charged = 0
        molecular_ion_present = False
        for v in dg.vertices:
            g = utils.graph_from_term(v.graph)
            charged = "+" in g.getGMLString()
            n_species += 1
            if charged:
                n_charged += 1
                if round(g.exactMass) == target_mass:
                    molecular_ion_present = True

        return molecule.exactMass, n_species, n_charged, molecular_ion_present

    def test_molecular_ion_produced_without_blowup(self):
        print("\n=== molecular-ion sanity check ===")
        print(f"  {'molecule':14s} {'M':>8s}  {'species':>7s}  {'charged':>7s}  M+. present")
        for name, smiles in MOLECULES:
            with self.subTest(molecule=name):
                exact, n_species, n_charged, has_mi = self._run_pipeline(name, smiles)
                print(f"  {name:14s} {exact:8.2f}  {n_species:7d}  {n_charged:7d}  {has_mi}")
                self.assertTrue(
                    has_mi,
                    f"{name}: intact molecular ion m/z {round(exact)} was not produced",
                )
                self.assertLess(
                    n_species,
                    MAX_SPECIES,
                    f"{name}: derivation graph blew up ({n_species} species >= {MAX_SPECIES})",
                )


if __name__ == "__main__":
    unittest.main()
