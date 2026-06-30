"""Unit tests for the Phase 0.1 explainability-ceiling metrics.

These exercise only the pure ``ceiling_metrics`` functions, so they run bare
(no ``mod``, no scientific stack) as well as inside the container.
"""
import random
import unittest

from src.data_generation.phase0 import ceiling_metrics as cm


class TestFormulaParsing(unittest.TestCase):
    def test_parses_spaced_nist_molform(self):
        self.assertEqual(cm.parse_formula("C3 H6 O"), {"C": 3, "H": 6, "O": 1})

    def test_parses_compact_formula_and_implicit_one(self):
        self.assertEqual(cm.parse_formula("C6H7N"), {"C": 6, "H": 7, "N": 1})

    def test_nominal_mass_matches_known_molecules(self):
        self.assertEqual(cm.nominal_mass_of(cm.parse_formula("C3 H6 O")), 58)   # acetone
        self.assertEqual(cm.nominal_mass_of(cm.parse_formula("C7 H8")), 92)     # toluene
        self.assertEqual(cm.nominal_mass_of(cm.parse_formula("C6 H7 N")), 93)   # aniline

    def test_unknown_element_raises(self):
        with self.assertRaises(KeyError):
            cm.nominal_mass_of({"Xx": 1})


class TestExplainedFraction(unittest.TestCase):
    def setUp(self):
        # base peak 43, M+• 58; one peak (40) is unexplained by mod_masses below.
        self.peaks = [(43.0, 100.0), (58.0, 40.0), (40.0, 10.0)]
        self.mod = {43, 58}

    def test_intensity_weighted(self):
        # explained intensity 140 of 150
        self.assertAlmostEqual(cm.explained_fraction(self.peaks, self.mod), 140 / 150)

    def test_count_fraction(self):
        self.assertAlmostEqual(
            cm.explained_fraction(self.peaks, self.mod, weighted=False), 2 / 3
        )

    def test_rounds_mz_to_nominal(self):
        # a Cl-like fragment whose mass sits just below the integer still matches.
        self.assertAlmostEqual(
            cm.explained_fraction([(34.97, 100.0)], {35}), 1.0
        )

    def test_empty_peaks_is_nan(self):
        self.assertTrue(cm.explained_fraction([], self.mod) != cm.explained_fraction([], self.mod))

    def test_select_peaks_filters_floor_and_ceiling(self):
        kept = cm.select_peaks(self.peaks, intensity_floor=20.0, mz_max=58)
        self.assertEqual(sorted(kept), [(43.0, 100.0), (58.0, 40.0)])


class TestFormulaReachableMasses(unittest.TestCase):
    def test_bounded_by_inventory_and_ceiling(self):
        pool = cm.formula_reachable_masses({"C": 3, "H": 6, "O": 1}, mass_ceiling=58)
        self.assertTrue(pool)                       # non-empty
        self.assertTrue(max(pool) <= 58)            # respects ceiling
        self.assertTrue(min(pool) >= 1)
        # every key reachable by C<=3, O<=1, H<=8 (6+extra_h)
        self.assertIn(12, pool)                     # bare C
        self.assertIn(16, pool)                     # O
        self.assertIn(58, pool)                     # full C3H6O

    def test_requires_a_heavy_atom(self):
        # pure-hydrogen masses (1,2,...) must not appear: no heavy atom.
        pool = cm.formula_reachable_masses({"H": 4}, mass_ceiling=10)
        self.assertEqual(pool, {})

    def test_multiplicity_is_positive(self):
        pool = cm.formula_reachable_masses({"C": 6, "H": 6}, mass_ceiling=78)
        self.assertTrue(all(v >= 1 for v in pool.values()))


class TestNullSampling(unittest.TestCase):
    def setUp(self):
        self.peaks = [(43.0, 100.0), (58.0, 40.0), (40.0, 10.0)]

    def test_null_in_unit_interval_and_reproducible(self):
        pool = cm.formula_reachable_masses({"C": 3, "H": 6, "O": 1}, 58)
        mean_a, ci_a, fr_a = cm.sample_null(pool, 3, self.peaks, draws=200, rng=random.Random(1))
        mean_b, _, _ = cm.sample_null(pool, 3, self.peaks, draws=200, rng=random.Random(1))
        self.assertEqual(mean_a, mean_b)            # seeded -> deterministic
        self.assertTrue(0.0 <= mean_a <= 1.0)
        self.assertLessEqual(ci_a[0], ci_a[1])
        self.assertEqual(len(fr_a), 200)

    def test_drawing_all_masses_explains_everything(self):
        # If the pool is exactly the explained peaks and k covers them, fraction=1.
        pool = {43: 1, 58: 1}
        mean, _, _ = cm.sample_null(pool, 2, [(43.0, 100.0), (58.0, 40.0)], draws=50)
        self.assertAlmostEqual(mean, 1.0)

    def test_uniform_pool_spans_ceiling(self):
        pool = cm.uniform_pool(58)
        self.assertEqual(min(pool), 1)
        self.assertEqual(max(pool), 58)
        self.assertTrue(all(v == 1 for v in pool.values()))


class TestCeilingWithCi(unittest.TestCase):
    def test_ceiling_is_raw_minus_null_mean(self):
        ceiling, (lo, hi) = cm.ceiling_with_ci(0.9, [0.2, 0.3, 0.4])
        self.assertAlmostEqual(ceiling, 0.9 - 0.3)
        self.assertLessEqual(lo, ceiling)
        self.assertLessEqual(ceiling, hi)

    def test_nan_raw_propagates(self):
        ceiling, _ = cm.ceiling_with_ci(float("nan"), [0.1])
        self.assertTrue(ceiling != ceiling)


class TestNitrogenRuleParity(unittest.TestCase):
    def test_nitrogen_free_even_mass_is_oe(self):
        # toluene M+• 92 (even, N=0) -> OE; tropylium 91 (odd) -> EE.
        self.assertEqual(cm.nitrogen_rule_parity(92, 0), "OE")
        self.assertEqual(cm.nitrogen_rule_parity(91, 0), "EE")

    def test_single_nitrogen_flips_mapping(self):
        # aniline M+• 93 (odd, N=1) -> OE; even mass -> EE.
        self.assertEqual(cm.nitrogen_rule_parity(93, 1), "OE")
        self.assertEqual(cm.nitrogen_rule_parity(66, 1), "EE")


if __name__ == "__main__":
    unittest.main()
