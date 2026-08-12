"""
Unit tests for the per-molecule migration scoping decision
(:func:`data_generation.core.strategy.migration_scope`).

Pure function of (heavy_count, reactive_fraction, thresholds, policy), so it runs in the fast
unit suite. It encodes a measured policy, and these tests pin the measurements rather than the
implementation: the saturated tail must be BOUNDED (capped) rather than either un-built or
un-bounded, and every molecule whose migration gains survive a chance correction must keep full
uncapped migration.

reactive_fraction values below are the real measured ones (verified against an independent
RDKit computation), so a change in the reactive-site definition that moved them would break
these tests -- which is the point.
"""
import unittest

from src.data_generation.core.strategy import (
    migration_scope,
    MIGRATION_TAIL_POLICIES,
    DEFAULT_TAIL_CAP,
)


# (name, heavy_count, reactive_fraction) -- measured on the neutral parent
TAIL = [                      # large AND sparsely reactive -> migration capped by default
    ("cholesterol", 28, 0.250),
    ("progesterone", 23, 0.478),
    ("stearic_acid", 20, 0.200),
    ("testosterone", 21, 0.429),
    ("cortisol", 26, 0.577),
    # Both of these escaped the tail while the cut sat at 0.6, and they were the only two
    # failures of the full migration-on rebuild (job 5806812): estrone peaked at 7.98 GB
    # against an 8 GB limit, aldosterone was killed at 12 h30 without writing a dump.
    ("estrone", 20, 0.650),
    ("aldosterone", 26, 0.654),   # highest rf retained in the tail
]
NOT_TAIL = [                  # must keep FULL UNCAPPED migration -- the cap is lossy here
    ("glucose", 12, 1.000),        # biggest chance-corrected win, p=3.7e-05
    ("limonene", 10, 0.900),       # p=3.3e-04
    ("sucrose", 23, 1.000),        # large but hetero-dense: p=0.005
    ("riboflavin", 27, 1.000),     # large but hetero-dense
    ("naphthalene", 10, 1.000),    # p=0.038
    ("toluene", 7, 1.000),
    ("n_octane", 8, 0.000),        # sparsely reactive but small: builds fine, no help needed
    ("decalin", 10, 0.000),
    ("cyclohexanol", 7, 0.286),    # capping THIS would cost 5.9% of its NIST intensity
    ("piperidine", 6, 0.500),      # capping THIS would cost 26.5% -- the worst case measured
    ("beta_carotene", 40, 0.800),  # first tail-eligible molecule above the cut -- must stay out
]


class TestMigrationScope(unittest.TestCase):

    def test_tail_molecules_are_capped_not_disabled_by_default(self):
        # The tail's problem was buildability, and the cap solves it: a steroid finishes in
        # ~1-1.5 h at cap 2 versus a >9 h timeout with no dump uncapped, producing a strict
        # superset of the no-migration result.
        for name, heavy, rf in TAIL:
            with self.subTest(molecule=name):
                scope = migration_scope(heavy, rf)
                self.assertTrue(scope.use_migration, f"{name}: expected migration ON ({scope.reason})")
                self.assertEqual(scope.cap, DEFAULT_TAIL_CAP, f"{name}: expected the tail cap")
                self.assertFalse(scope.use_gate, f"{name}: the gate is not the default lever")
                self.assertIn("tail", scope.reason.lower())

    def test_non_tail_molecules_keep_full_uncapped_migration(self):
        for name, heavy, rf in NOT_TAIL:
            with self.subTest(molecule=name):
                scope = migration_scope(heavy, rf)
                self.assertTrue(scope.use_migration, f"{name}: expected migration ON ({scope.reason})")
                self.assertIsNone(scope.cap, f"{name}: the cap is LOSSY outside the tail")
                self.assertFalse(scope.use_gate, f"{name}: gate must be off outside the tail")

    def test_both_clauses_are_required(self):
        # large + dense-reactive (sucrose-like) -> uncapped;  small + sparse (octane-like) ->
        # uncapped; only large AND sparse is the tail.
        self.assertIsNone(migration_scope(23, 1.000).cap, "size alone must not select the tail")
        self.assertIsNone(migration_scope(8, 0.000).cap, "low rf alone must not select the tail")
        self.assertEqual(migration_scope(23, 0.400).cap, DEFAULT_TAIL_CAP,
                         "large AND sparse is the tail")

    def test_boundary_is_exclusive_on_rf_and_inclusive_on_size(self):
        # rf strictly below the cut is tail; exactly at the cut is not.
        self.assertIsNotNone(migration_scope(20, 0.659).cap)
        self.assertIsNone(migration_scope(20, 0.660).cap)
        # heavy count at the floor counts as large.
        self.assertIsNotNone(migration_scope(18, 0.300).cap)
        self.assertIsNone(migration_scope(17, 0.300).cap)

    def test_estrone_is_inside_the_cut_not_exactly_on_it(self):
        # Regression guard for an off-by-one that looks harmless. estrone's rf is exactly
        # 13/20 = 0.65, and the rf test is ``>=``, so a cut of 0.65 leaves it on uncapped
        # migration -- i.e. changes nothing about the failure it was meant to fix. The cut
        # must sit strictly above 0.65.
        self.assertIsNone(migration_scope(20, 0.650, max_reactive_fraction=0.65).cap,
                          "a 0.65 cut is a no-op for estrone -- this is the trap")
        self.assertIsNotNone(migration_scope(20, 0.650).cap,
                             "estrone must be capped at the shipped default")
        self.assertIsNotNone(migration_scope(26, 17 / 26).cap,
                             "aldosterone (17/26) must be capped at the shipped default")

    # ---- structure clause: size OR ring count -------------------------------------------
    # (name, heavy, rf, cyclomatic) -- measured on the neutral parent
    FUSED_TAIL = [
        ("decalin", 10, 0.000, 2),        # 79.4 s vs decane's 5.13 s at identical heavy/rf
        ("camphor", 11, 0.364, 2),        # 45 min uncapped in the corpus build
        ("tricyclic_C10", 10, 0.000, 3),  # CC1(C)C2CC3C1C3(C)C2 -- 13 h16 uncapped
        ("terpenoid_decoy", 16, 0.125, 3),  # the 16 h decoys from job 5824027
    ]
    MONOCYCLIC_KEEP_FULL = [
        # The cap is MEASURED LOSSY here, which is why the threshold is 2 and not 1.
        ("piperidine", 6, 0.500, 1),      # cap 3 costs 26.5% of NIST intensity
        ("cyclohexanol", 7, 0.286, 1),    # cap 3 costs 5.9%
    ]
    ACYCLIC_KEEP_FULL = [
        ("octane", 8, 0.000, 0),          # 2.38 s -- needs no intervention
        ("decane", 10, 0.000, 0),         # 5.13 s
    ]

    def test_fused_rings_enter_the_tail_regardless_of_size(self):
        for name, heavy, rf, cyc in self.FUSED_TAIL:
            with self.subTest(molecule=name):
                scope = migration_scope(heavy, rf, cyclomatic=cyc)
                self.assertEqual(scope.cap, DEFAULT_TAIL_CAP,
                                 f"{name}: fused + sparsely reactive is the tail ({scope.reason})")
                self.assertIn("cyclomatic", scope.reason)

    def test_monocycles_keep_full_migration_because_the_cap_is_lossy_there(self):
        for name, heavy, rf, cyc in self.MONOCYCLIC_KEEP_FULL:
            with self.subTest(molecule=name):
                self.assertIsNone(migration_scope(heavy, rf, cyclomatic=cyc).cap,
                                  f"{name}: capping a monocycle drops real peaks")

    def test_small_acyclic_chains_keep_full_migration(self):
        for name, heavy, rf, cyc in self.ACYCLIC_KEEP_FULL:
            with self.subTest(molecule=name):
                self.assertIsNone(migration_scope(heavy, rf, cyclomatic=cyc).cap,
                                  f"{name}: cheap already; lowering min_heavy would sweep it in")

    def test_ring_clause_boundary_is_two(self):
        self.assertIsNone(migration_scope(10, 0.000, cyclomatic=1).cap)
        self.assertIsNotNone(migration_scope(10, 0.000, cyclomatic=2).cap)

    def test_ring_clause_still_obeys_the_reactive_fraction_clause(self):
        # Hetero-dense fused molecules are where migration's chance-corrected wins live
        # (sucrose p=0.005, riboflavin) -- the ring clause must not drag them in.
        for name, heavy, rf, cyc in (("sucrose", 23, 1.000, 2), ("riboflavin", 27, 1.000, 3)):
            with self.subTest(molecule=name):
                self.assertIsNone(migration_scope(heavy, rf, cyclomatic=cyc).cap,
                                  f"{name}: dense-reactive must keep full migration")

    def test_ring_clause_can_be_disabled(self):
        self.assertIsNone(migration_scope(10, 0.000, cyclomatic=3, min_cyclomatic=0).cap,
                          "min_cyclomatic<=0 reverts to size-only scoping")

    def test_size_clause_still_fires_for_acyclic_long_chains(self):
        # stearic acid: cyclomatic 0, caught by the size clause alone.
        scope = migration_scope(20, 0.200, cyclomatic=0)
        self.assertEqual(scope.cap, DEFAULT_TAIL_CAP)
        self.assertIn("heavy", scope.reason)

    def test_tail_cap_is_configurable(self):
        scope = migration_scope(28, 0.250, tail_cap=4)
        self.assertEqual(scope.cap, 4)
        self.assertIn("4", scope.reason)

    def test_off_policy_disables_the_tail_entirely(self):
        # Still offered, because the tail's TPR gain is indistinguishable from chance (p=0.56)
        # even though it is now affordable.
        for name, heavy, rf in TAIL:
            with self.subTest(molecule=name):
                scope = migration_scope(heavy, rf, policy="off")
                self.assertFalse(scope.use_migration)
                self.assertIsNone(scope.cap)

    def test_gate_policy_runs_the_gate_on_the_tail_only(self):
        scope = migration_scope(28, 0.250, policy="gate")
        self.assertTrue(scope.use_migration)
        self.assertTrue(scope.use_gate)
        self.assertIsNone(scope.cap, "the gate and the cap are alternatives, not cumulative")
        # outside the tail, "gate" must not switch the gate on
        scope = migration_scope(12, 1.000, policy="gate")
        self.assertTrue(scope.use_migration)
        self.assertFalse(scope.use_gate)

    def test_full_policy_keeps_migration_everywhere_unbounded(self):
        for name, heavy, rf in TAIL:
            with self.subTest(molecule=name):
                scope = migration_scope(heavy, rf, policy="full")
                self.assertTrue(scope.use_migration)
                self.assertFalse(scope.use_gate)
                self.assertIsNone(scope.cap)

    def test_min_heavy_zero_disables_scoping(self):
        scope = migration_scope(28, 0.250, min_heavy=0)
        self.assertTrue(scope.use_migration)
        self.assertFalse(scope.use_gate)
        self.assertIsNone(scope.cap)
        self.assertIn("disabled", scope.reason)

    def test_unknown_policy_raises(self):
        with self.assertRaises(ValueError):
            migration_scope(28, 0.250, policy="sometimes")

    def test_policies_constant_matches_accepted_values(self):
        for policy in MIGRATION_TAIL_POLICIES:
            with self.subTest(policy=policy):
                migration_scope(28, 0.250, policy=policy)  # must not raise

    def test_reason_is_reported_for_every_branch(self):
        for kwargs in ({"heavy_count": 28, "reactive_fraction": 0.250},
                       {"heavy_count": 12, "reactive_fraction": 1.000},
                       {"heavy_count": 8, "reactive_fraction": 0.000},
                       {"heavy_count": 28, "reactive_fraction": 0.250, "policy": "off"},
                       {"heavy_count": 28, "reactive_fraction": 0.250, "policy": "gate"}):
            with self.subTest(**kwargs):
                reason = migration_scope(**kwargs).reason
                self.assertTrue(reason and isinstance(reason, str))
                self.assertIn("migration", reason.lower())


if __name__ == "__main__":
    unittest.main()
