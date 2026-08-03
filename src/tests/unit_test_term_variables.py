"""
Unit tests for the Stage-2 term-variable encoder change: distinct placeholder names
(``_A``, ``_B``, ...) authored in a rule stay INDEPENDENT term variables, and
``apply_constraints`` constrains each one, while a nameless wildcard and the legacy
``_A``-only rules keep their previous (collapse) behaviour.

Runs in the fast unit suite (a single tiny DG apply); it imports mod so it executes in
the container via run/ci_cd/unit_test.sh.
"""
import unittest

import mod

from src.data_generation import utils
from src.data_generation.utils.term_transfers import encode_vertex_label
from src.data_generation.utils.constrain import _placeholders_in_rule


LS = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)


def _fire_on_OC(term_rule):
    """Apply a term rule to an O(+.)-C substrate; return product label-multisets."""
    g = mod.Graph.fromGMLString(
        'graph [ node [ id 0 label "a(O, 1, 1)" ] node [ id 1 label "a(C, 0, 0)" ]'
        ' edge [ source 0 target 1 label "e(p(0))" ] ]',
        name="OC", add=False,
    )
    dg = mod.DG(graphDatabase=[g], labelSettings=LS)
    b = dg.build()
    return [",".join(sorted(v.stringLabel for v in t.graph.vertices))
            for e in b.apply([g], term_rule) for t in e.targets]


class TestEncodeVertexLabel(unittest.TestCase):
    def test_named_placeholders_preserved(self):
        self.assertEqual(encode_vertex_label("_A"), ("_A", 0, 0))
        self.assertEqual(encode_vertex_label("_B"), ("_B", 0, 0))
        self.assertEqual(encode_vertex_label("_B+."), ("_B", 1, 1))
        self.assertEqual(encode_vertex_label("_R1-"), ("_R1", -1, 0))

    def test_nameless_wildcard_collapses_to_A(self):
        self.assertEqual(encode_vertex_label("*")[0], "_A")
        self.assertEqual(encode_vertex_label("*+.")[0], "_A")

    def test_real_elements_unchanged(self):
        self.assertEqual(encode_vertex_label("C+."), ("C", 1, 1))
        self.assertEqual(encode_vertex_label("O-"), ("O", -1, 0))
        self.assertEqual(encode_vertex_label("Cl"), ("Cl", 0, 0))


class TestPlaceholderConstraints(unittest.TestCase):
    def test_finds_all_distinct_placeholders(self):
        r = mod.Rule.fromDFS(s="[_A+.]1[_B]2>>[_A]1[_B+.]2", name="ab")
        self.assertEqual(_placeholders_in_rule(r, "A"), ["A", "B"])

    def test_falls_back_to_default_when_no_placeholder(self):
        r = mod.Rule.fromDFS(s="[C+.]1>>[C+.]1", name="c")
        self.assertEqual(_placeholders_in_rule(r, "A"), ["A"])

    def test_apply_constraints_constrains_every_placeholder(self):
        r = mod.Rule.fromDFS(s="[_A+.]1[_B]2>>[_A]1[_B+.]2", name="ab")
        constrained = utils.apply_constraints([r], {"C", "O"})[0]
        gml = constrained.getGMLString()
        self.assertIn('label "_A"', gml)
        self.assertIn('label "_B"', gml)


class TestIndependentVariablesFire(unittest.TestCase):
    def test_independent_AB_rule_fires_cross_element(self):
        # [_A]/[_B] independent -> a term rule that matches O at one position and C at the
        # other, so it fires on O(+.)-C.
        r = mod.Rule.fromDFS(s="[_A+.]1[_B]2>>[_A]1[_B+.]2", name="ab")
        term_rule = utils.term_from_rule(utils.apply_constraints([r], {"C", "O"})[0])
        left = sorted(v.stringLabel for v in term_rule.left.vertices)
        self.assertEqual(left, ["a(_A, 1, 1)", "a(_B, 0, 0)"])
        self.assertTrue(_fire_on_OC(term_rule), "independent _A/_B rule should fire on O-C")

    def test_single_A_rule_forces_same_element(self):
        # Legacy behaviour: reusing _A forces both atoms to the same element, so it does
        # NOT fire on the cross-element O-C substrate.
        r = mod.Rule.fromDFS(s="[_A+.]1[_A]2>>[_A]1[_A+.]2", name="aa")
        term_rule = utils.term_from_rule(utils.apply_constraints([r], {"C", "O"})[0])
        left = sorted(v.stringLabel for v in term_rule.left.vertices)
        self.assertEqual(left, ["a(_A, 0, 0)", "a(_A, 1, 1)"])
        self.assertEqual(_fire_on_OC(term_rule), [], "reused _A must force same element")


if __name__ == "__main__":
    unittest.main()
