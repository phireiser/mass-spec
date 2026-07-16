"""
Integration test: run the real MØD fragmentation pipeline on toluene and check
it against the NIST reference spectrum (from the Parquet store, outputs/nist_spectra/,
looked up by SMILES).

Unlike the mocked unit tests in test_data_generation_utils.py, this exercises
the actual `mod` engine end-to-end, so it is slow and skipped unless explicitly
enabled. Run it via run/integration_test.sh.

Toluene's textbook EI-MS fragmentation: the molecular ion (m/z 92) loses a
methyl hydrogen to give the very stable tropylium cation C7H7+ (m/z 91, the
spectrum's base peak), which loses C2H2 to give the cyclopentadienyl cation
C5H5+ (m/z 65), which further fragments to the cyclopropenyl cation C3H3+
(m/z 39). All four masses are confirmed as major peaks in the NIST spectrum.
"""

import os
import unittest

import mod

from src.data_generation import utils
from src.data_generation.analysis import describe
from src.data_generation.rules import fragmentation, ionization
from src.data_generation.core import strategy


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/integration_test.sh)",
)
class TestTolueneFragmentation(unittest.TestCase):

    EXPECTED_FRAGMENT_MASSES = {92, 91, 65, 39}

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        mod.config.common.numThreads = 1

        # Aromatic SMILES: the ring rides through term mode as the inert bond
        # e(ar), and the curated aromatic rules (benzylAllyl_*) match it directly.
        molecule = mod.Graph.fromSMILES("Cc1ccccc1", "toluene")
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

        cls.dg = dg
        cls.molecule_term = molecule_term
        cls.stats = describe.spectrum_statistic(dg, molecule_term)

    def test_produces_more_than_the_molecular_ion(self):
        mod_masses = self.stats["MØD masses"]
        self.assertGreater(len(mod_masses), 1, f"no fragment ions were generated, only: {mod_masses}")

    def test_known_fragment_masses_occur(self):
        mod_masses = set(self.stats["MØD masses"])
        missing = self.EXPECTED_FRAGMENT_MASSES - mod_masses
        self.assertFalse(missing, f"expected fragment masses not produced by MOD: {sorted(missing)}")

    def test_known_fragment_masses_match_nist_reference(self):
        ground_truth_masses = set(self.stats["ground_truth masses"])
        missing = self.EXPECTED_FRAGMENT_MASSES - ground_truth_masses
        self.assertFalse(missing, f"expected masses missing from NIST reference spectrum: {sorted(missing)}")

    def test_overlaps_with_nist_reference_spectrum(self):
        overlap = set(self.stats["MØD masses"]) & set(self.stats["ground_truth masses"])
        self.assertTrue(overlap, "MØD-generated masses have no overlap with the NIST reference spectrum")


if __name__ == "__main__":
    unittest.main()
