"""
Regression test for the term-space charge/mass helpers used by the strategy
predicates (data_generation.core.predicates).

To speed up data generation, `charge_bound` and `amu_bound` were changed to read
each fragment's net charge and exact mass straight from its term-mode vertex
labels (`net_charge_from_term` / `exact_mass_from_term`) instead of round-tripping
every fragment back into a string-mode molecule -- the old path canonicalised a
SMILES string per fragment just to `count('+')`, and rebuilt the molecule just to
read `.exactMass`.

This test runs the real fragmentation pipeline on a fixed molecule and pins, for
*every* generated species, that the fast term-space values agree with the old
round-trip values. If the two ever diverge, the optimization changed behaviour.

It also pins concrete chemistry for toluene: the species charges form the set
{0, +1} and the intact molecular ion (charge +1 at m/z 92) is present.

Like the other integration tests this drives the real MOD engine, so it is slow
and skipped unless RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh).

SMILES are written in Kekule form (explicit single/double bonds): term_from_graph
has no term encoding for aromatic bonds.
"""

import os
import unittest
from collections import Counter

import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization
from src.data_generation.core import strategy


MOLECULE_NAME = "toluene"
MOLECULE_SMILES = "CC1=CC=CC=C1"

# Fragmentation rounds for this test. The asserted charge properties (charge set
# {0, +1}; M+. at m/z 92) are independent of cascade depth; 2 exercises the charge
# bookkeeping on at least one secondary fragment while avoiding the ~2x cost of the
# default 5 (which only adds cheap tail rounds for toluene). Data generation uses
# make_fwd_strategy's default of 5.
FRAG_REPEAT = 2


def _reference_charge(term_graph):
    """Old charge path: round-trip to a string-mode molecule, count SMILES signs.

    Returns None for non-molecules, mirroring the old `if g.isMolecule` guard.
    """
    g = utils.graph_from_term(term_graph)
    if not g.isMolecule:
        return None
    return g.smiles.count("+") - g.smiles.count("-")


def _reference_mass(term_graph):
    """Old mass path: round-trip to a string-mode molecule, read exactMass.

    Returns None for non-molecules, mirroring the old `if g.isMolecule` guard.
    """
    g = utils.graph_from_term(term_graph)
    if not g.isMolecule:
        return None
    return g.exactMass


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh)",
)
class TestChargeCounting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        mod.config.common.numThreads = 1

        molecule = mod.Graph.fromSMILES(MOLECULE_SMILES, MOLECULE_NAME)
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
            frag_repeat=FRAG_REPEAT,
        )
        dg.build().execute(strat)

        cls.dg = dg
        cls.molecular_ion_mass = round(molecule.exactMass)  # toluene: 92
        cls.species = [v.graph for v in dg.vertices]

    def test_pipeline_produced_species(self):
        self.assertGreater(len(self.species), 1, "pipeline produced no fragments")

    def test_term_charge_matches_smiles_reference(self):
        """The fast term-space charge equals the old SMILES-sign charge, per species."""
        for g in self.species:
            with self.subTest(species=g.name):
                fast = utils.net_charge_from_term(g)
                ref = _reference_charge(g)
                if ref is not None:  # ref only defined for string-mode molecules
                    self.assertEqual(
                        fast, ref,
                        f"{g.name}: term charge {fast} != SMILES-reference charge {ref}",
                    )

    def test_term_mass_matches_roundtrip_reference(self):
        """The fast term-space exact mass equals the old round-trip exactMass, per species."""
        for g in self.species:
            with self.subTest(species=g.name):
                fast = utils.exact_mass_from_term(g)
                ref = _reference_mass(g)
                if ref is not None:
                    self.assertIsNotNone(fast, f"{g.name}: term mass is None but reference is {ref}")
                    self.assertAlmostEqual(
                        fast, ref, places=6,
                        msg=f"{g.name}: term mass {fast} != round-trip mass {ref}",
                    )

    def test_charge_distribution_is_neutral_or_singly_positive(self):
        """Toluene EI fragmentation yields only neutral and +1 species."""
        charges = Counter(utils.net_charge_from_term(g) for g in self.species)
        print(f"\n  {MOLECULE_NAME} charge histogram: {dict(sorted(charges.items()))}")
        self.assertEqual(
            set(charges), {0, 1},
            f"unexpected charge states for {MOLECULE_NAME}: {dict(charges)}",
        )

    def test_molecular_ion_is_singly_charged(self):
        """The intact molecular ion (m/z 92) is present and carries charge +1."""
        molecular_ions = [
            g for g in self.species
            if utils.net_charge_from_term(g) == 1
            and round(utils.exact_mass_from_term(g) or -1) == self.molecular_ion_mass
        ]
        self.assertTrue(
            molecular_ions,
            f"no singly-charged molecular ion at m/z {self.molecular_ion_mass} was produced",
        )


if __name__ == "__main__":
    unittest.main()
