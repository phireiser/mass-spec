"""Unit tests for the Phase-1 discrimination spectrum ops.

These exercise only the pure ``spectrum_ops`` functions, so they run bare (no
pyarrow/rdkit/torch) as well as inside the container. They also pin the binning
semantics to ``machine_learning.data.bin_spectrum``.
"""
import math
import unittest

from src.data_generation.analysis.discrimination import spectrum_ops as so


class TestBinSpectrum(unittest.TestCase):
    def test_sums_intensities_in_same_integer_bin(self):
        # Two peaks that floor to the same bin add before sqrt.
        vec = so.bin_spectrum([(10.0, 9.0), (10.4, 7.0)], sqrt_and_l2=False)
        self.assertEqual(vec[10], 16.0)

    def test_floor_bin_index(self):
        vec = so.bin_spectrum([(10.9, 1.0)], sqrt_and_l2=False)
        self.assertEqual(vec[10], 1.0)
        self.assertEqual(vec[11], 0.0)

    def test_drops_out_of_range_peaks(self):
        vec = so.bin_spectrum([(2000.0, 5.0), (-1.0, 5.0)], sqrt_and_l2=False)
        self.assertEqual(math.fsum(vec), 0.0)

    def test_sqrt_then_l2_unit_norm(self):
        vec = so.bin_spectrum([(10.0, 9.0), (20.0, 16.0)])
        # sqrt -> [3, 4] -> L2 -> [0.6, 0.8]
        self.assertAlmostEqual(vec[10], 0.6, places=6)
        self.assertAlmostEqual(vec[20], 0.8, places=6)
        self.assertAlmostEqual(math.sqrt(math.fsum(v * v for v in vec)), 1.0, places=6)

    def test_matches_reference_bin_spectrum_when_torch_available(self):
        peaks = [(10.0, 9.0), (10.4, 7.0), (55.0, 100.0), (200.0, 3.0)]
        try:
            from src.machine_learning.data import bin_spectrum as ref
        except Exception:  # torch not installed in this environment
            self.skipTest("machine_learning.data.bin_spectrum unavailable")
        ref_vec = ref(peaks, so.MZ_MIN, so.MZ_MAX, so.BIN_WIDTH, sqrt_and_l2=True).tolist()
        ours = so.bin_spectrum(peaks)
        for a, b in zip(ours, ref_vec):
            self.assertAlmostEqual(a, b, places=5)


class TestCosine(unittest.TestCase):
    def test_identical_is_one(self):
        v = so.bin_spectrum([(10.0, 9.0), (20.0, 16.0)])
        self.assertAlmostEqual(so.cosine(v, v), 1.0, places=6)

    def test_disjoint_is_zero(self):
        a = so.bin_spectrum([(10.0, 1.0)])
        b = so.bin_spectrum([(20.0, 1.0)])
        self.assertAlmostEqual(so.cosine(a, b), 0.0, places=6)

    def test_zero_vector_is_zero(self):
        self.assertEqual(so.cosine([0.0, 0.0], [1.0, 1.0]), 0.0)

    def test_cosine_from_peaks_roundtrip(self):
        peaks = [(31.0, 100.0), (29.0, 40.0)]
        self.assertAlmostEqual(so.cosine_from_peaks(peaks, peaks), 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
