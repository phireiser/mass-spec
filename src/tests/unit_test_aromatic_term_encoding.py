"""
Unit test for the inert aromatic bond encoding (Phase A of the aromaticity-aware
term-mode refactor).

Aromatic bonds are now carried through term mode as the ground term ``e(ar)``
instead of the old ``"__error2"`` reject sentinel, so an aromatic molecule (or
fragment) can be round-tripped term<->string without being kekulised first. No
rule authored with ``p(0)/p(p(0))/...`` can match ``e(ar)``, so an aromatic ring
is protected from the generic (integer electron-pushing) rules by construction.

This pins that the encoding constant, the decoder, and the term<->string graph
round-trip all agree, and that mass and aromaticity survive the round-trip: mass
is bond-order agnostic, and aromaticity is restored because ``e(ar)`` decodes back
to mod's ``":"`` bond.

Runs in the mol-spectro container (``mod`` is imported at module load, like the
other tests under ``src/tests``). No derivation graph is built, so it is fast.
"""

import unittest

import mod

from src.data_generation import utils
from src.data_generation.utils.term_transfers import (
    term_bond_from_bond_type,
    decode_edge_label,
)


class TestAromaticTermEncoding(unittest.TestCase):

    def test_aromatic_bond_maps_to_inert_term(self):
        # the "__error2" reject sentinel is gone; aromatic -> inert e(ar)
        self.assertEqual(term_bond_from_bond_type[mod.BondType.Aromatic], "ar")

    def test_decode_edge_label_round_trips_aromatic(self):
        # inverse mapping: e(ar) -> mod's string-mode aromatic bond ":"
        self.assertEqual(decode_edge_label("e(ar)"), ":")
        # the integer bonds are untouched
        self.assertEqual(decode_edge_label("e(p(0))"), "-")
        self.assertEqual(decode_edge_label("e(p(p(0)))"), "=")

    def test_term_from_graph_does_not_reject_aromatic(self):
        benzene = mod.Graph.fromSMILES("c1ccccc1", name="benzene")
        self.assertTrue(
            any(e.bondType == mod.BondType.Aromatic for e in benzene.edges),
            "precondition: mod should perceive the ring as aromatic",
        )
        n_aromatic = sum(e.bondType == mod.BondType.Aromatic for e in benzene.edges)
        # previously raised ValueError ("no term-mode encoding")
        term = utils.term_from_graph(benzene)
        # exactly the aromatic ring bonds become e(ar); the C-H bonds stay single.
        # No edge carries the old "__error2" sentinel.
        n_ar_terms = sum("e(ar)" in e.stringLabel for e in term.edges)
        self.assertEqual(n_ar_terms, n_aromatic)
        self.assertGreater(n_ar_terms, 0)
        self.assertFalse(any("__error" in e.stringLabel for e in term.edges))

    def test_graph_from_term_preserves_mass_and_aromaticity(self):
        benzene = mod.Graph.fromSMILES("c1ccccc1", name="benzene")
        restored = utils.graph_from_term(utils.term_from_graph(benzene))
        # mass is bond-order agnostic -> must match exactly
        self.assertAlmostEqual(restored.exactMass, benzene.exactMass, places=6)
        # aromaticity is restored on the way back (e(ar) -> ":")
        self.assertTrue(restored.isMolecule)
        self.assertTrue(
            any(e.bondType == mod.BondType.Aromatic for e in restored.edges)
        )


if __name__ == "__main__":
    unittest.main()
