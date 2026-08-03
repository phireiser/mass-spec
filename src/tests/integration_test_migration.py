"""
Integration test for the fully delocalized charge model (charge/radical migration
rules interleaved with fragmentation). Drives the real MOD engine, so it is skipped
unless RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh).

Confirms, on a substituted aromatic and a heteroatom ester, that enabling migration:
  1. keeps the net charge in {0, +1} -- a hop moves one + (or one .) across a bond, so
     it must never manufacture a di-cation (the charge_bound invariant),
  2. still produces the intact molecular ion M+.,
  3. is strictly ADDITIVE -- every charged m/z reachable without migration is still
     reachable with it (migration only opens new charge sites, it removes none), and
  4. does not blow the derivation graph past the MAX_SPECIES guard.

Masses/charges are read with the term-space helpers (no graph_from_term round-trip),
which is also the safe path for the charged aromatic species migration can create.
"""
import os
import unittest

import mod

from src.data_generation import utils
from src.data_generation.rules import fragmentation, ionization, build_migration_rules
from src.data_generation.core import strategy


MOLECULES = [
    ("toluene", "Cc1ccccc1"),
    ("ethyl_acetate", "CC(=O)OCC"),
]

# Toluene's classic EI fragments (M+., tropylium, cyclopentadienyl, cyclopropenyl);
# migration must not lose any of them.
TOLUENE_ACCEPTANCE = {92, 91, 65, 39}

MAX_SPECIES = 500
FRAG_REPEAT = 5


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh)",
)
class TestChargeMigration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        mod.config.common.numThreads = 1

    def _run(self, name, smiles, use_migration):
        """Return (n_species, charge_set, charged_mz_set, parent_mz)."""
        molecule = utils.graph_from_smiles(smiles, name)
        molecule_term = utils.term_from_graph(molecule)
        aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

        ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
        dg = mod.DG(graphDatabase=[molecule_term], labelSettings=ls)

        ionization_terms = [utils.term_from_rule(r) for r in utils.apply_constraints(ionization, aoc)]
        fragmentation_terms = [utils.term_from_rule(r) for r in utils.apply_constraints(fragmentation, aoc)]
        migration_terms = build_migration_rules(sorted(aoc - {"H"})) if use_migration else []

        strat = strategy.make_fwd_strategy(
            derivation_graph=dg,
            universe=molecule_term,
            ionization=ionization_terms,
            fragmentation=fragmentation_terms,
            migration=migration_terms,
            max_mass=molecule.exactMass,
            frag_repeat=FRAG_REPEAT,
        )
        dg.build().execute(strat)

        parent = round(molecule.exactMass)
        charge_set = set()
        charged_mz = set()
        for g in dg.graphDatabase:
            ch = utils.net_charge_from_term(g)
            charge_set.add(ch)
            m = utils.exact_mass_from_term(g)
            if m is not None and ch >= 1:
                charged_mz.add(int(round(m)))
        return dg.numVertices, charge_set, charged_mz, parent

    def test_migration_is_additive_and_charge_bounded(self):
        print("\n=== charge-migration integration check ===")
        for name, smiles in MOLECULES:
            with self.subTest(molecule=name):
                n0, chg0, mz0, parent = self._run(name, smiles, use_migration=False)
                n1, chg1, mz1, _ = self._run(name, smiles, use_migration=True)
                print(f"  {name:14s} base DG={n0:3d} mz={len(mz0):2d} | "
                      f"mig DG={n1:3d} mz={len(mz1):2d} | new={sorted(mz1 - mz0)}")

                # (1) charge stays in {0, +1}; migration never makes a di-cation
                self.assertTrue(
                    chg1.issubset({0, 1}),
                    f"{name}: migration produced out-of-range charges {sorted(chg1)}",
                )
                # (2) intact molecular ion still present
                self.assertIn(parent, mz1, f"{name}: M+. m/z {parent} lost with migration")
                # (3) strictly additive: no baseline charged m/z disappears
                lost = mz0 - mz1
                self.assertEqual(lost, set(), f"{name}: migration LOST charged m/z {sorted(lost)}")
                # (4) no derivation-graph blow-up
                self.assertLess(
                    n1, MAX_SPECIES,
                    f"{name}: migration blew up the DG ({n1} >= {MAX_SPECIES})",
                )

    def test_toluene_acceptance_peaks_survive_migration(self):
        _, _, mz, parent = self._run("toluene", "Cc1ccccc1", use_migration=True)
        missing = TOLUENE_ACCEPTANCE - mz
        self.assertEqual(
            missing, set(),
            f"toluene: migration is missing acceptance peaks {sorted(missing)} (have {sorted(mz)})",
        )


if __name__ == "__main__":
    unittest.main()
