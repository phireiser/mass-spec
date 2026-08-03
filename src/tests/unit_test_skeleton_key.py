"""
Unit tests for :func:`data_generation.utils.skeleton_key`, the projection
``species -> skeleton`` that the migration multiplicity cap budgets on.

The two properties the cap's correctness rests on:

* it must COLLAPSE charge/radical placement variants of one structure onto one key -- if it
  did not, every variant would get its own budget and the cap would prune nothing;
* it must NOT collapse structurally different skeletons, nor different electron classes,
  onto one key -- a merge silently over-prunes, which would show up as "the cap is too
  tight" and be attributed to the wrong cause.
"""
import unittest

import mod

from src.data_generation import utils


LS = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)


def term_graph(atoms, bonds, name="g"):
    """Build a term-mode graph from ``atoms`` = [(symbol, charge, radical), ...] and
    ``bonds`` = [(i, j, order_term), ...]. Kept local so the tests state their molecules
    explicitly rather than depending on the SMILES/encoder path."""
    nodes = "".join(
        f'node [ id {i} label "a({s}, {c}, {r})" ] ' for i, (s, c, r) in enumerate(atoms)
    )
    edges = "".join(f'edge [ source {i} target {j} label "e({o})" ] ' for i, j, o in bonds)
    return mod.Graph.fromGMLString(f"graph [ {nodes}{edges} ]", name=name, add=False)


SINGLE, DOUBLE = "p(0)", "p(p(0))"


class TestSkeletonKey(unittest.TestCase):

    def test_charge_placement_variants_share_one_key(self):
        # C+(0)-C(1)-C(2)  vs  C(0)-C(1)-C+(2): same skeleton, charge moved. One budget.
        a = term_graph([("C", 1, 0), ("C", 0, 0), ("C", 0, 0)],
                       [(0, 1, SINGLE), (1, 2, SINGLE)], "a")
        b = term_graph([("C", 0, 0), ("C", 0, 0), ("C", 1, 0)],
                       [(0, 1, SINGLE), (1, 2, SINGLE)], "b")
        self.assertEqual(utils.skeleton_key(a), utils.skeleton_key(b))

    def test_radical_placement_variants_share_one_key(self):
        a = term_graph([("C", 1, 1), ("C", 0, 0), ("C", 0, 0)],
                       [(0, 1, SINGLE), (1, 2, SINGLE)], "a")
        b = term_graph([("C", 1, 0), ("C", 0, 0), ("C", 0, 1)],
                       [(0, 1, SINGLE), (1, 2, SINGLE)], "b")
        self.assertEqual(utils.skeleton_key(a), utils.skeleton_key(b))

    def test_different_electron_class_does_not_share_a_key(self):
        # Odd-electron (charge 1, radical 1) vs even-electron cation (charge 1, radical 0) on
        # the same skeleton. Migration conserves both, so they can never interconvert; merging
        # them would let one class eat the other's budget.
        odd = term_graph([("C", 1, 1), ("C", 0, 0)], [(0, 1, SINGLE)], "odd")
        even = term_graph([("C", 1, 0), ("C", 0, 0)], [(0, 1, SINGLE)], "even")
        self.assertNotEqual(utils.skeleton_key(odd), utils.skeleton_key(even))

    def test_different_bond_order_does_not_share_a_key(self):
        single = term_graph([("C", 1, 0), ("C", 0, 0)], [(0, 1, SINGLE)], "s")
        double = term_graph([("C", 1, 0), ("C", 0, 0)], [(0, 1, DOUBLE)], "d")
        self.assertNotEqual(utils.skeleton_key(single), utils.skeleton_key(double))

    def test_different_element_does_not_share_a_key(self):
        cc = term_graph([("C", 1, 0), ("C", 0, 0)], [(0, 1, SINGLE)], "cc")
        co = term_graph([("C", 1, 0), ("O", 0, 0)], [(0, 1, SINGLE)], "co")
        self.assertNotEqual(utils.skeleton_key(cc), utils.skeleton_key(co))

    def test_branching_is_distinguished_from_a_chain(self):
        # n-butyl vs isobutyl cation skeletons: same formula, same |V| and |E|, different
        # connectivity. A key that merged these would over-prune.
        chain = term_graph([("C", 1, 0), ("C", 0, 0), ("C", 0, 0), ("C", 0, 0)],
                           [(0, 1, SINGLE), (1, 2, SINGLE), (2, 3, SINGLE)], "chain")
        branch = term_graph([("C", 1, 0), ("C", 0, 0), ("C", 0, 0), ("C", 0, 0)],
                            [(0, 1, SINGLE), (1, 2, SINGLE), (1, 3, SINGLE)], "branch")
        self.assertNotEqual(utils.skeleton_key(chain), utils.skeleton_key(branch))

    def test_key_is_isomorphism_invariant_under_vertex_renumbering(self):
        # Same molecule, ids permuted. WL is invariant by construction; if this ever failed
        # the cap would SPLIT one skeleton across several budgets and prune nothing.
        a = term_graph([("C", 1, 0), ("O", 0, 0), ("C", 0, 0)],
                       [(0, 1, SINGLE), (1, 2, SINGLE)], "a")
        b = term_graph([("C", 0, 0), ("O", 0, 0), ("C", 1, 0)],
                       [(2, 1, SINGLE), (1, 0, SINGLE)], "b")
        self.assertEqual(utils.skeleton_key(a), utils.skeleton_key(b))

    def test_key_reports_size_and_electron_class_in_the_leading_fields(self):
        # The cap reads key[0] to decide whether a skeleton is in the parent-mass class, so
        # the leading field must be the vertex count.
        g = term_graph([("C", 1, 1), ("O", 0, 0), ("C", 0, 0)],
                       [(0, 1, SINGLE), (1, 2, SINGLE)], "g")
        key = utils.skeleton_key(g)
        self.assertEqual(key[0], 3, "leading field must be |V|")
        self.assertEqual(key[1], 2, "second field must be |E|")
        self.assertEqual(key[2], 1, "third field must be net charge")
        self.assertEqual(key[3], 1, "fourth field must be radical count")

    def test_key_is_hashable(self):
        g = term_graph([("C", 1, 0), ("C", 0, 0)], [(0, 1, SINGLE)], "g")
        self.assertIsInstance({utils.skeleton_key(g): 1}, dict)


if __name__ == "__main__":
    unittest.main()
