"""
Unit tests for the charge/radical migration rule construction (fully delocalized
charge model). These only build the rules (no derivation graph), so they run in the
fast unit suite; they lock in the term-mode authoring that the Stage-0 mod probe
validated: independent element variables, a preserved radical slot, a bond-order
variable, and the heavy-atom constraint that keeps charge/radical off hydrogen.
"""
import unittest

import mod
from src.data_generation.rules import build_migration_rules
from src.data_generation.rules.migration import _CHARGE_HOP_GML, _RADICAL_HOP_GML


class TestMigrationRuleConstruction(unittest.TestCase):
    def test_builds_two_rules_named(self):
        rules = build_migration_rules(["C", "O", "N"])
        self.assertEqual([r.name for r in rules], ["charge migration", "radical migration"])
        for r in rules:
            self.assertEqual(r.left.numVertices, 2)
            self.assertEqual(r.right.numVertices, 2)

    def test_hydrogen_is_stripped_from_allowlist(self):
        # H must never be a charge/radical acceptor: a(H, 1, .) is a spurious bridging
        # proton. build_migration_rules drops H even if passed.
        gml = _CHARGE_HOP_GML % (
            '\n    constrainLabelAny [ label "_A" labels [ label "C" ] ]'
        )  # sanity that the template is well-formed on its own
        self.assertIn('label "_A"', gml)
        rules = build_migration_rules(["H", "C", "O"])
        self.assertEqual(len(rules), 2)
        for r in rules:
            g = r.getGMLString()
            # the constraint allowlist names C and O but never H
            self.assertIn('label "C"', g)
            self.assertIn('label "O"', g)
            self.assertNotIn('label "H"', g)

    def test_empty_heavy_atoms_is_noop(self):
        # A hydrogen-only universe (no heavy atoms) yields no migration rules rather than
        # an invalid empty constrainLabelAny block.
        self.assertEqual(build_migration_rules([]), [])
        self.assertEqual(build_migration_rules(["H"]), [])

    def test_templates_carry_independent_and_preserved_variables(self):
        # Charge hop: element vars _A/_B independent, radical slot _R/_S preserved,
        # bond var _X. Radical hop: charge slot _C/_D preserved.
        self.assertIn("a(_A, 1, _R)", _CHARGE_HOP_GML)
        self.assertIn("a(_B, 0, _S)", _CHARGE_HOP_GML)
        self.assertIn("e(_X)", _CHARGE_HOP_GML)
        self.assertIn("a(_A, _C, 1)", _RADICAL_HOP_GML)
        self.assertIn("a(_B, _D, 0)", _RADICAL_HOP_GML)

    def test_rules_parse_under_term_label_settings(self):
        # The rules must be valid term-mode rules (mod.Rule.fromGMLString already ran in
        # build_migration_rules; assert they expose a left/right as expected).
        charge_hop, radical_hop = build_migration_rules(["C", "O"])
        # charge hop moves +1 from id0 to id1; both ids present on both sides
        self.assertEqual(charge_hop.numVertices, 2)
        self.assertEqual(radical_hop.numVertices, 2)


if __name__ == "__main__":
    unittest.main()
