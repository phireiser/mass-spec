"""
Regression test for the NIST reference-spectrum lookup on stereo-dependent molecules.

The store is keyed SMILES -> InChIKey -> CAS. The term encoding ``a(symbol, charge, radical)``
carries no stereo descriptors, so reconstructing the SMILES from the term graph
(``graph_from_term(molecule).smiles``) canonicalises to a DIFFERENT InChIKey for any molecule
whose identity depends on stereochemistry -- and the lookup silently returns ``[]``.

That was not hypothetical: it zeroed the ground truth for every saccharide in both arms of an
A/B comparison, so real differences were reported as "0.00 coverage, unmeasurable". Sucrose has
46 reference peaks by its original SMILES and 0 by the round-trip; glucose 94 vs 0. Riboflavin
(no stereocentres) is unaffected at 49 vs 49, which is why only the sugars ever looked empty.

Touches the Parquet store but builds no derivation graph, so it is cheap; it is an integration
test because it needs the real store.
"""
import os
import unittest
from pathlib import Path

import mod

from src.data_generation import utils
from src.data_generation.analysis import describe
from src.project_paths import shared_path


# (name, original SMILES, has stereocentres that the term round-trip drops)
STEREO_MOLECULES = [
    ("sucrose", "OC[C@H]1OC(O[C@H]2OC(CO)C(O)C(O)C2O)C(O)C(O)C1O", True),
    ("glucose", "OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@H]1O", True),
    ("riboflavin", "CC1=CC2=C(C=C1C)N(CC(O)C(O)C(O)CO)C1=NC(=O)NC(=O)C1=N2", False),
]


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "reads the real Parquet store; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh)",
)
class TestStereoSpectrumLookup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        cls.parquet = Path(str(shared_path("PARQUET_DIR_REL")))

    def test_original_smiles_resolves_reference_peaks(self):
        """The molecules must be present in the store under their ORIGINAL SMILES."""
        for name, smiles, _ in STEREO_MOLECULES:
            with self.subTest(molecule=name):
                peaks = utils.get_spectra_by_smiles(smiles, self.parquet)
                self.assertGreater(
                    len(peaks), 0,
                    f"{name}: store has no peaks for its original SMILES -- the fixture "
                    f"molecule is missing, so this test cannot detect the regression",
                )

    def test_term_roundtrip_loses_stereo_lookup(self):
        """Pins the ROOT CAUSE: the round-trip SMILES fails to resolve where stereo matters.

        If this ever starts passing for the stereo molecules, the term encoding gained
        stereo (or the store became stereo-insensitive) and ``_ground_truth_smiles`` can be
        simplified -- it is not a bug to fix here, but it must not go unnoticed.
        """
        for name, smiles, drops_stereo in STEREO_MOLECULES:
            with self.subTest(molecule=name):
                molecule = utils.graph_from_smiles(smiles, name)
                roundtrip = utils.graph_from_term(utils.term_from_graph(molecule)).smiles
                peaks = utils.get_spectra_by_smiles(roundtrip, self.parquet)
                if drops_stereo:
                    self.assertEqual(
                        len(peaks), 0,
                        f"{name}: round-trip SMILES unexpectedly resolved ({len(peaks)} "
                        f"peaks) -- stereo may now survive the term encoding",
                    )
                else:
                    self.assertGreater(
                        len(peaks), 0,
                        f"{name}: has no stereocentres, so the round-trip must still resolve",
                    )

    def test_spectrum_statistic_uses_passed_smiles(self):
        """The fix: passing ``smiles`` yields a non-empty ground truth; omitting it does not.

        Uses an empty DG (no build) -- only the ground-truth side of the summary is under
        test, and it is independent of the MOD masses.
        """
        ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
        for name, smiles, drops_stereo in STEREO_MOLECULES:
            if not drops_stereo:
                continue
            with self.subTest(molecule=name):
                molecule = utils.graph_from_smiles(smiles, name)
                molecule_term = utils.term_from_graph(molecule)
                dg = mod.DG(graphDatabase=[molecule_term], labelSettings=ls)

                with_smiles = describe.summarize_spectrum_overlap(
                    dg, molecule_term, smiles=smiles
                )
                self.assertGreater(
                    with_smiles["ground_truth support"], 0,
                    f"{name}: passing the original SMILES still found no reference peaks",
                )

                without = describe.summarize_spectrum_overlap(dg, molecule_term)
                self.assertEqual(
                    without["ground_truth support"], 0,
                    f"{name}: the round-trip fallback unexpectedly found peaks; if the "
                    f"encoding changed, relax this pin",
                )


if __name__ == "__main__":
    unittest.main()
