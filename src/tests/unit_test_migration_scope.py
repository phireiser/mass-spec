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
    ("cortisol", 26, 0.577),   # highest rf retained in the tail
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
    ("estrone", 20, 0.650),        # just above the rf cut -- the boundary case
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
        self.assertIsNotNone(migration_scope(20, 0.599).cap)
        self.assertIsNone(migration_scope(20, 0.600).cap)
        # heavy count at the floor counts as large.
        self.assertIsNotNone(migration_scope(18, 0.300).cap)
        self.assertIsNone(migration_scope(17, 0.300).cap)

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
