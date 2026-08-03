"""
Integration tests for the two levers that make the fully delocalized charge model affordable:
the TERMINAL-ROUND TRIM and the MULTIPLICITY CAP. Drives the real MOD engine, so it is
skipped unless RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh).

The trim is claimed to be FREE and the cap is claimed to be BOUNDED-AND-LOSSY, and those two
claims need different tests:

* the trim must leave the integer mass set EXACTLY unchanged while shrinking the graph -- it
  drops migration from the final repeat round, where a hop's product has its reactant's exact
  mass and can never be an educt, so it is unobservable by construction;
* the cap must shrink the graph, must actually bind (at most N migration-produced variants per
  parent-mass skeleton), and must never manufacture a mass or a charge state.

The cap is deliberately NOT asserted lossless: it is free on decalin and the aromatics but
costs 5.9% of cyclohexanol's NIST intensity and 26.5% of piperidine's, which is exactly why
``migration_scope`` confines it to the saturated tail.
"""
import os
import unittest

import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization, build_migration_rules
from src.data_generation.core import strategy


FRAG_REPEAT = 5


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh)",
)
class TestMigrationCapAndTrim(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        mod.config.common.numThreads = 1

    def _run(self, name, smiles, cap=None, trim=True):
        """Build one forward DG. Returns (n_species, charge_set, charged_mz_set, dg, term)."""
        molecule = utils.graph_from_smiles(smiles, name)
        molecule_term = utils.term_from_graph(molecule)
        aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

        ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
        dg = mod.DG(graphDatabase=[molecule_term], labelSettings=ls)

        ionization_terms = [utils.term_from_rule(r)
                            for r in utils.apply_constraints(ionization, aoc)]
        fragmentation_terms = [utils.term_from_rule(r)
                               for r in utils.apply_constraints(fragmentation, aoc)]
        migration_terms = build_migration_rules(sorted(aoc - {"H"}))

        strat = strategy.make_fwd_strategy(
            derivation_graph=dg,
            universe=molecule_term,
            ionization=ionization_terms,
            fragmentation=fragmentation_terms,
            migration=migration_terms,
            migration_cap=cap,
            trim_terminal_migration=trim,
            max_mass=molecule.exactMass,
            frag_repeat=FRAG_REPEAT,
        )
        dg.build().execute(strat)

        charge_set, charged_mz = set(), set()
        for g in dg.graphDatabase:
            ch = utils.net_charge_from_term(g)
            charge_set.add(ch)
            m = utils.exact_mass_from_term(g)
            if m is not None and ch >= 1:
                charged_mz.add(int(round(m)))
        return dg.numVertices, charge_set, charged_mz, dg, molecule_term

    # ---------------------------------------------------------------- terminal-round trim

    def test_trim_shrinks_the_graph_and_preserves_the_mass_set_exactly(self):
        # The headline claim, and the reason the trim is safe to ship on by default. Measured
        # at corpus scale as identical on 12/12 molecules; here on one aromatic and one
        # saturated molecule, which are the two regimes.
        for name, smiles in (("toluene", "CC1=CC=CC=C1"), ("n_octane", "CCCCCCCC")):
            with self.subTest(molecule=name):
                n_untrimmed, _, mz_untrimmed, _, _ = self._run(name, smiles, trim=False)
                n_trimmed, chg, mz_trimmed, _, _ = self._run(name, smiles, trim=True)
                print(f"\n  {name}: untrimmed DG={n_untrimmed} -> trimmed DG={n_trimmed}")
                self.assertEqual(
                    mz_trimmed, mz_untrimmed,
                    f"{name}: the trim changed the mass set -- lost "
                    f"{sorted(mz_untrimmed - mz_trimmed)}, gained "
                    f"{sorted(mz_trimmed - mz_untrimmed)}; it is supposed to be free",
                )
                self.assertLess(n_trimmed, n_untrimmed,
                                f"{name}: the trim removed no species ({n_trimmed} !< {n_untrimmed})")
                self.assertTrue(chg.issubset({0, 1}))

    def test_trim_is_a_no_op_at_frag_repeat_one(self):
        # At k=1 the trim would degenerate to "migration off", which is lossy, so it must be
        # guarded off. Exercised through the strategy builder rather than by reading the flag.
        molecule = utils.graph_from_smiles("CC(=O)C", "acetone")
        term = utils.term_from_graph(molecule)
        aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)
        ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
        mz = {}
        for trim in (False, True):
            dg = mod.DG(graphDatabase=[term], labelSettings=ls)
            strat = strategy.make_fwd_strategy(
                derivation_graph=dg,
                universe=term,
                ionization=[utils.term_from_rule(r)
                            for r in utils.apply_constraints(ionization, aoc)],
                fragmentation=[utils.term_from_rule(r)
                               for r in utils.apply_constraints(fragmentation, aoc)],
                migration=build_migration_rules(sorted(aoc - {"H"})),
                trim_terminal_migration=trim,
                max_mass=molecule.exactMass,
                frag_repeat=1,
            )
            dg.build().execute(strat)
            mz[trim] = dg.numVertices
        self.assertEqual(mz[True], mz[False],
                         "the trim must be inert at frag_repeat=1, not silently disable migration")

    # -------------------------------------------------------------------- multiplicity cap

    def test_cap_binds_and_shrinks_the_graph(self):
        cap = 2
        n_uncapped, _, mz_uncapped, _, _ = self._run("n_octane", "CCCCCCCC")
        n_capped, chg, mz_capped, dg, term = self._run("n_octane", "CCCCCCCC", cap=cap)
        print(f"\n  n_octane: uncapped DG={n_uncapped} -> cap {cap} DG={n_capped}")
        self.assertLess(n_capped, n_uncapped,
                        f"cap {cap} removed no species ({n_capped} !< {n_uncapped})")
        # The cap is additive-negative only: it can never invent a mass the uncapped run
        # lacked, because the capped graph is a subgraph of the uncapped one.
        self.assertEqual(mz_capped - mz_uncapped, set(),
                         f"cap manufactured masses {sorted(mz_capped - mz_uncapped)}")
        self.assertTrue(chg.issubset({0, 1}),
                        f"cap produced out-of-range charges {sorted(chg)}")

    def test_cap_bounds_variants_per_parent_mass_skeleton(self):
        # The invariant the knob actually promises. Counted over the parent-mass class only,
        # which is what the predicate budgets; and counting only what migration produced is
        # impossible from the finished graph, so this asserts the WEAKER, checkable bound:
        # the capped run must hold strictly fewer parent-mass variants than the uncapped one.
        cap = 2
        _, _, _, dg_unc, term = self._run("n_octane", "CCCCCCCC")
        _, _, _, dg_cap, _ = self._run("n_octane", "CCCCCCCC", cap=cap)

        def parent_class_variants(dg, n_parent):
            counts = {}
            for g in dg.graphDatabase:
                key = utils.skeleton_key(g)
                if key[0] == n_parent:
                    counts[key] = counts.get(key, 0) + 1
            return counts

        n_parent = term.numVertices
        unc = parent_class_variants(dg_unc, n_parent)
        cap_counts = parent_class_variants(dg_cap, n_parent)
        self.assertTrue(unc, "no parent-mass skeletons found -- the test molecule is wrong")
        print(f"\n  n_octane parent-mass max multiplicity: "
              f"uncapped={max(unc.values())} capped={max(cap_counts.values())}")
        self.assertLess(max(cap_counts.values()), max(unc.values()),
                        "the cap did not reduce the worst parent-mass multiplicity")

    def test_cap_leaves_fragment_skeletons_uncapped(self):
        # The measured-best shape: budget only the parent-mass class, where MOD's quadratic
        # bucket cost lives, and leave fragments alone. A cap that also bit fragments would
        # show up as fragment skeletons capped at N.
        cap = 1
        _, _, _, dg, term = self._run("n_octane", "CCCCCCCC", cap=cap)
        n_parent = term.numVertices
        fragment_counts = {}
        for g in dg.graphDatabase:
            key = utils.skeleton_key(g)
            if key[0] != n_parent:
                fragment_counts[key] = fragment_counts.get(key, 0) + 1
        self.assertTrue(
            fragment_counts and max(fragment_counts.values()) > cap,
            "every fragment skeleton is at or below the cap, so the cap is not "
            "parent-mass-scoped as intended",
        )


if __name__ == "__main__":
    unittest.main()
