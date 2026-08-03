"""
Integration test for the migration PROFIT GATE (molecule-scoped scope guard for the large
saturated tail). Drives the real MOD engine, so it is skipped unless
RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh).

The gate keeps a charge/radical hop only when the decoration lands on a reactive site,
pruning the saturated-sigma charge-wandering that blows the DG up. It confirms:
  1. on a saturated hydrocarbon (n-octane) the gate strictly SHRINKS the migration DG
     (the whole point) while keeping the intact M+. and charge in {0, +1};
  2. on an aromatic (toluene) -- where every ring atom is reactive -- forcing the gate on
     preserves the classic acceptance peaks {92, 91, 65, 39}, i.e. the gate never removes a
     productive hop when the whole framework is reactive.

Note the gate is deliberately NOT additive (that is its purpose on the saturated tail: it
drops the unproductive isomers), so unlike the ungated migration test we do not assert
"loses no baseline peak" for octane -- only the M+./charge invariants and the DG shrink.
"""
import os
import unittest

import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization, build_migration_rules
from src.data_generation.core import strategy


TOLUENE_ACCEPTANCE = {92, 91, 65, 39}
FRAG_REPEAT = 5


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh)",
)
class TestMigrationProfitGate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        mod.config.common.numThreads = 1

    def _run(self, name, smiles, gate):
        """Build with migration always ON; ``gate`` toggles the profit gate. Returns
        (n_species, charge_set, charged_mz_set, parent_mz)."""
        molecule = utils.graph_from_smiles(smiles, name)
        molecule_term = utils.term_from_graph(molecule)
        aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

        ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
        dg = mod.DG(graphDatabase=[molecule_term], labelSettings=ls)

        ionization_terms = [utils.term_from_rule(r) for r in utils.apply_constraints(ionization, aoc)]
        fragmentation_terms = [utils.term_from_rule(r) for r in utils.apply_constraints(fragmentation, aoc)]
        migration_terms = build_migration_rules(sorted(aoc - {"H"}))

        strat = strategy.make_fwd_strategy(
            derivation_graph=dg,
            universe=molecule_term,
            ionization=ionization_terms,
            fragmentation=fragmentation_terms,
            migration=migration_terms,
            gate_migration=gate,
            max_mass=molecule.exactMass,
            frag_repeat=FRAG_REPEAT,
        )
        dg.build().execute(strat)

        parent = round(molecule.exactMass)
        charge_set, charged_mz = set(), set()
        for g in dg.graphDatabase:
            ch = utils.net_charge_from_term(g)
            charge_set.add(ch)
            m = utils.exact_mass_from_term(g)
            if m is not None and ch >= 1:
                charged_mz.add(int(round(m)))
        return dg.numVertices, charge_set, charged_mz, parent

    def test_gate_shrinks_saturated_dg_and_keeps_invariants(self):
        n_full, _, mz_full, parent = self._run("n_octane", "CCCCCCCC", gate=False)
        n_gated, chg_gated, mz_gated, _ = self._run("n_octane", "CCCCCCCC", gate=True)
        print(f"\n  n_octane: full DG={n_full} -> gated DG={n_gated}")
        # (1) the gate strictly prunes the saturated charge-wandering
        self.assertLess(n_gated, n_full,
                        f"gate did not shrink octane DG ({n_gated} !< {n_full})")
        # (2) intact molecular ion survives the gate
        self.assertIn(parent, mz_gated, f"gate lost M+. m/z {parent} on octane")
        # (3) no di-cation manufactured
        self.assertTrue(chg_gated.issubset({0, 1}),
                        f"gate produced out-of-range charges {sorted(chg_gated)}")

    def test_gate_preserves_aromatic_acceptance_peaks(self):
        # toluene: every ring atom is reactive, so forcing the gate on must keep the
        # classic peaks -- the gate only prunes where the framework is saturated.
        _, chg, mz, _ = self._run("toluene", "Cc1ccccc1", gate=True)
        missing = TOLUENE_ACCEPTANCE - mz
        self.assertEqual(missing, set(),
                         f"gated toluene missing acceptance peaks {sorted(missing)} "
                         f"(have {sorted(mz)})")
        self.assertTrue(chg.issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
