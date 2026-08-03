"""
Unit tests for the migration profit gate's reactive-site predicate
(:func:`data_generation.utils.charge_radical_on_reactive_site`). Pure function over a
term-mode graph's labels -- no derivation graph -- so it runs in the fast unit suite and
locks in the semantics the gate depends on:

* the migrated ``+`` / radical is "reactive" when it lands ON or ADJACENT to unsaturation
  (double/triple/aromatic bond) or a heteroatom -- the alpha/allylic/benzylic shell where
  EI cleavages initiate;
* a saturated-sigma interior placement (alkane middle carbon) is NOT reactive -- this is the
  charge-wandering the gate prunes on the large saturated tail;
* ``want_charge`` selects charge vs radical; no decorated atom is vacuously reactive.

Graphs are authored directly in term GML (``a(sym, charge, radical)`` / ``e(order)``), the
same encoding :func:`term_from_graph` emits, so the vertex/edge ``stringLabel`` the predicate
parses is exactly the production one.
"""
import unittest

import mod
from src.data_generation.utils import charge_radical_on_reactive_site

SINGLE = "e(p(0))"
DOUBLE = "e(p(p(0)))"
AROM = "e(ar)"


def _term_graph(nodes, edges):
    """Build a term-mode graph from ``nodes`` [(id, "sym,charge,radical"), ...] and
    ``edges`` [(src, tgt, edge_label), ...]."""
    s = "graph [\n"
    for vid, atom in nodes:
        s += f'  node [ id {vid} label "a({atom})" ]\n'
    for src, tgt, lbl in edges:
        s += f'  edge [ source {src} target {tgt} label "{lbl}" ]\n'
    s += "]\n"
    return mod.Graph.fromGMLString(s, add=False)


class TestReactiveSitePredicate(unittest.TestCase):
    def test_alkane_interior_charge_is_not_reactive(self):
        # propane cation, + on the middle carbon: no heteroatom, no unsaturation, all
        # neighbours saturated carbons -> the exact hop the gate must prune.
        g = _term_graph(
            [(0, "C, 0, 0"), (1, "C, 1, 0"), (2, "C, 0, 0")],
            [(0, 1, SINGLE), (1, 2, SINGLE)],
        )
        self.assertFalse(charge_radical_on_reactive_site(g, want_charge=True))

    def test_charge_on_heteroatom_is_reactive(self):
        g = _term_graph(
            [(0, "O, 1, 0"), (1, "C, 0, 0")],
            [(0, 1, SINGLE)],
        )
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=True))

    def test_charge_alpha_to_heteroatom_is_reactive(self):
        # + on a carbon single-bonded to O (alpha cleavage site)
        g = _term_graph(
            [(0, "C, 1, 0"), (1, "O, 0, 0")],
            [(0, 1, SINGLE)],
        )
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=True))

    def test_charge_on_double_bond_is_reactive(self):
        g = _term_graph(
            [(0, "C, 1, 0"), (1, "C, 0, 0")],
            [(0, 1, DOUBLE)],
        )
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=True))

    def test_allylic_charge_is_reactive(self):
        # + on a carbon single-bonded to a C=C (allylic cation)
        g = _term_graph(
            [(0, "C, 1, 0"), (1, "C, 0, 0"), (2, "C, 0, 0")],
            [(0, 1, SINGLE), (1, 2, DOUBLE)],
        )
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=True))

    def test_benzylic_charge_is_reactive(self):
        # + on a CH2 single-bonded to an aromatic ring carbon (benzylic -> tropylium route)
        g = _term_graph(
            [(0, "C, 1, 0"), (1, "C, 0, 0"), (2, "C, 0, 0")],
            [(0, 1, SINGLE), (1, 2, AROM)],
        )
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=True))

    def test_radical_interior_is_not_reactive_but_on_unsaturation_is(self):
        interior = _term_graph(
            [(0, "C, 0, 0"), (1, "C, 0, 1"), (2, "C, 0, 0")],
            [(0, 1, SINGLE), (1, 2, SINGLE)],
        )
        self.assertFalse(charge_radical_on_reactive_site(interior, want_charge=False))
        on_unsat = _term_graph(
            [(0, "C, 0, 1"), (1, "C, 0, 0")],
            [(0, 1, DOUBLE)],
        )
        self.assertTrue(charge_radical_on_reactive_site(on_unsat, want_charge=False))

    def test_charge_predicate_ignores_radical_and_vice_versa(self):
        # Chain C+(0)-C(1)-C.(2)=C(3): the charge sits on a saturated-interior carbon
        # (neighbour 1 is not on the unsaturation), while the radical sits on the double
        # bond. The charge test looks only at the charged atom (not reactive); the radical
        # test only at the radical atom (on the double bond -> reactive).
        g = _term_graph(
            [(0, "C, 1, 0"), (1, "C, 0, 0"), (2, "C, 0, 1"), (3, "C, 0, 0")],
            [(0, 1, SINGLE), (1, 2, SINGLE), (2, 3, DOUBLE)],
        )
        self.assertFalse(charge_radical_on_reactive_site(g, want_charge=True))
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=False))

    def test_no_decorated_atom_is_vacuously_reactive(self):
        # neutral, closed-shell alkane: nothing to place, so the gate must not veto it
        g = _term_graph(
            [(0, "C, 0, 0"), (1, "C, 0, 0")],
            [(0, 1, SINGLE)],
        )
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=True))
        self.assertTrue(charge_radical_on_reactive_site(g, want_charge=False))


if __name__ == "__main__":
    unittest.main()
