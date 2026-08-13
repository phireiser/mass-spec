"""Behaviour of the analysis modules that turn runs into reported numbers.

``metrics`` (coverage) and ``cost_model`` (the cost/N* extrapolation) had no test
at all, yet their output is quoted directly in the thesis. The censoring
behaviour in particular is load-bearing: censored tasks are excluded from the
per-bin mean, which makes the projection a LOWER bound, and a silent regression
there would understate the corpus cost without anything looking wrong.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.data_generation.analysis import cost_model as cm
from src.data_generation.analysis import metrics as M


class TestSetMetrics(unittest.TestCase):
    def test_dice_is_two_times_overlap_over_total(self):
        self.assertEqual(M.dice_coefficient([1, 2, 3], [2, 3, 4]), 2 * 2 / 6)

    def test_dice_of_identical_sets_is_one(self):
        self.assertEqual(M.dice_coefficient([1, 2], [2, 1]), 1.0)

    def test_dice_of_disjoint_sets_is_zero(self):
        self.assertEqual(M.dice_coefficient([1], [2]), 0.0)

    def test_dice_of_two_empty_sets_is_zero_not_a_crash(self):
        self.assertEqual(M.dice_coefficient([], []), 0.0)

    def test_duplicates_do_not_change_the_score(self):
        """Inputs are mass lists; a mass repeated by two rules is still one mass."""
        self.assertEqual(M.dice_coefficient([1, 1, 2], [1, 2, 2]),
                         M.dice_coefficient([1, 2], [1, 2]))

    def test_overlap_normalises_by_the_smaller_set(self):
        # A subset scores 1.0 even though Dice does not.
        self.assertEqual(M.overlap_coefficient([1, 2], [1, 2, 3, 4]), 1.0)
        self.assertLess(M.dice_coefficient([1, 2], [1, 2, 3, 4]), 1.0)

    def test_overlap_with_an_empty_set_is_zero_not_a_crash(self):
        self.assertEqual(M.overlap_coefficient([], [1, 2]), 0.0)


class TestCoverageStats(unittest.TestCase):
    def test_tpr_is_the_fraction_of_reference_masses_recovered(self):
        stats = M.coverage_stats(mod_masses=[91, 92, 65], ref_masses=[91, 92, 39, 65])
        self.assertEqual(stats["TPR"], 3 / 4)
        self.assertEqual(stats["MØD support"], 3)
        self.assertEqual(stats["Ref support"], 4)

    def test_masses_are_coerced_to_int_and_sorted(self):
        stats = M.coverage_stats(mod_masses=[92.0, 91.4], ref_masses=["65"])
        self.assertEqual(stats["MØD masses"], [91, 92])
        self.assertEqual(stats["Ref masses"], [65])

    def test_empty_reference_gives_zero_tpr_not_a_crash(self):
        """A molecule absent from NIST must not kill a corpus sweep."""
        self.assertEqual(M.coverage_stats([91], [])["TPR"], 0.0)

    def test_extra_mod_masses_cost_dice_but_not_tpr(self):
        """Over-generation is penalised by Dice, invisible to TPR -- report both."""
        strict = M.coverage_stats([91], [91])
        noisy = M.coverage_stats([91] + list(range(200, 260)), [91])
        self.assertEqual(strict["TPR"], noisy["TPR"])
        self.assertGreater(strict["Dice"], noisy["Dice"])


class TestCostLogParsing(unittest.TestCase):
    def test_hms_accepts_both_time_v_formats(self):
        self.assertEqual(cm._hms("1:02:03"), 3723.0)   # h:mm:ss
        self.assertAlmostEqual(cm._hms("2:03.50"), 123.5)  # m:ss.ss
        self.assertEqual(cm._hms("42"), 42.0)

    def test_hms_rejects_garbage(self):
        self.assertIsNone(cm._hms("not-a-time"))

    def _write_log(self, directory: Path, stem: str, body: str) -> Path:
        path = directory / f"{stem}.out"
        path.write_text(body, encoding="utf-8")
        return path

    def test_parse_log_extracts_name_wall_and_rss(self):
        with TemporaryDirectory() as tmp:
            log = self._write_log(Path(tmp), "7__toluene", (
                "mol spectrum of 108-88-3\n"
                "migration: ON\n"
                "\tElapsed (wall clock) time (h:mm:ss or m:ss): 0:01:30\n"
                "\tMaximum resident set size (kbytes): 2097152\n"))
            row = cm.parse_log(log)
        self.assertEqual(row["name"], "108-88-3")
        self.assertEqual(row["wall_s"], 90.0)
        self.assertEqual(row["rss_gib"], 2.0)
        self.assertFalse(row["censored"])
        self.assertFalse(row["capped"])

    def test_a_log_without_a_time_block_is_censored(self):
        """No `time -v` output means the task was killed: cost is a lower bound."""
        with TemporaryDirectory() as tmp:
            log = self._write_log(Path(tmp), "3__big", "mol spectrum of 57-88-5\n")
            row = cm.parse_log(log)
        self.assertTrue(row["censored"])
        self.assertIsNone(row["wall_s"])

    def test_capped_is_read_from_the_migration_scope_line(self):
        with TemporaryDirectory() as tmp:
            log = self._write_log(Path(tmp), "1__steroid", (
                "mol spectrum of 57-88-5\nmigration: CAP 2 (min_heavy)\n"))
            self.assertTrue(cm.parse_log(log)["capped"])

    def test_name_falls_back_to_the_log_filename_stem(self):
        with TemporaryDirectory() as tmp:
            log = self._write_log(Path(tmp), "12__mystery", "nothing useful\n")
            self.assertEqual(cm.parse_log(log)["name"], "mystery")

    def test_unreadable_log_yields_an_empty_row(self):
        self.assertEqual(cm.parse_log(Path("/nonexistent/x.out")), {})


class TestCostBinning(unittest.TestCase):
    BINS = [{"bin": "small", "lo": 0, "hi": 9, "store_count": 100},
            {"bin": "large", "lo": 10, "hi": 99, "store_count": 10}]

    def test_bin_of_picks_the_containing_bin(self):
        self.assertEqual(cm.bin_of(5, self.BINS), "small")
        self.assertEqual(cm.bin_of(10, self.BINS), "large")

    def test_bin_of_is_inclusive_at_both_edges(self):
        self.assertEqual(cm.bin_of(0, self.BINS), "small")
        self.assertEqual(cm.bin_of(9, self.BINS), "small")

    def test_bin_of_returns_none_outside_every_bin(self):
        self.assertIsNone(cm.bin_of(1000, self.BINS))

    _next_id = 0

    def _row(self, nheavy, wall_s, censored=False, byts=1000, rss=1.0, name=None):
        """A row shaped like ``arm_rows`` output (which always sets ``name``)."""
        TestCostBinning._next_id += 1
        return {"name": name or f"mol-{TestCostBinning._next_id}",
                "nheavy": nheavy, "wall_s": wall_s, "censored": censored,
                "bytes": byts, "rss_gib": rss}

    def test_summarize_reweights_by_store_frequency(self):
        """1 h per small molecule x 100 in the store == 100 core-hours."""
        rows = [self._row(5, 3600.0)]
        out = cm.summarize_arm("arm", rows, self.BINS)
        self.assertAlmostEqual(out["per_bin"]["small"]["mean_wall_s"], 3600.0)
        self.assertAlmostEqual(out["projected_corpus_core_h"], 100.0)
        self.assertEqual(out["store_molecules_covered"], 100)
        self.assertFalse(out["is_lower_bound"], "nothing censored, so it is an estimate")

    def test_censored_rows_are_excluded_from_the_mean(self):
        """The projection must be a lower bound, so a killed task cannot pull it down."""
        rows = [self._row(5, 3600.0), self._row(5, None, censored=True)]
        out = cm.summarize_arm("arm", rows, self.BINS)
        bin_small = out["per_bin"]["small"]
        self.assertEqual(bin_small["n"], 2)
        self.assertEqual(bin_small["n_censored"], 1)
        self.assertAlmostEqual(bin_small["mean_wall_s"], 3600.0)
        # The headline number must announce itself as a floor, not an estimate.
        self.assertTrue(out["is_lower_bound"])
        self.assertAlmostEqual(out["censoring_rate"], 0.5)

    def test_a_fully_censored_bin_contributes_no_hours(self):
        rows = [self._row(5, None, censored=True)]
        out = cm.summarize_arm("arm", rows, self.BINS)
        self.assertIsNone(out["per_bin"]["small"]["mean_wall_s"])
        self.assertAlmostEqual(out["projected_corpus_core_h"], 0.0)
        self.assertTrue(out["is_lower_bound"])

    def test_bins_with_no_samples_are_omitted(self):
        out = cm.summarize_arm("arm", [self._row(5, 60.0)], self.BINS)
        self.assertIn("small", out["per_bin"])
        self.assertNotIn("large", out["per_bin"])


if __name__ == "__main__":
    unittest.main()
