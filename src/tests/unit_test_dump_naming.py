"""CAS-first dump stem resolution (src/data_generation/utils/dump_naming.py).

Regression cover for the class of bug that silently broke run/analysis/generated_fwd_dg.sh:
the corpus was renamed to CAS, but readers still asked for the human name and got
FileNotFoundError on a dump that was sitting right there under 108-88-3.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.data_generation.utils import codec
from src.data_generation.utils import dump_naming as dn

# A legacy (pre-compression) dump: plain .pkl/.dmp plus a zero-byte .done marker.
LEGACY_SUFFIXES = (".pkl", ".dmp", dn.DONE_SUFFIX)


def _touch_dump(directory: Path, stem: str, suffixes=LEGACY_SUFFIXES) -> None:
    for suffix in suffixes:
        (directory / f"{stem}{suffix}").write_bytes(b"")


def _touch_compressed_dump(directory: Path, stem: str) -> None:
    """A dump as it is written now: compressed pair plus the marker."""
    for suffix in dn.DUMP_BASE_SUFFIXES:
        with codec.open_write(directory / f"{stem}{suffix}") as handle:
            handle.write(b"payload")
    dn.write_done_marker(directory, stem, dmp_bytes=7, pkl_bytes=7)


class TestDumpStemCandidates(unittest.TestCase):
    def test_cas_comes_first(self):
        self.assertEqual(dn.dump_stem_candidates("toluene", "108-88-3"),
                         ["108-88-3", "toluene"])

    def test_name_only_when_cas_is_missing(self):
        for cas in (None, "", "   "):
            with self.subTest(cas=cas):
                self.assertEqual(dn.dump_stem_candidates("toluene", cas), ["toluene"])

    def test_identical_cas_and_name_is_not_repeated(self):
        self.assertEqual(dn.dump_stem_candidates("108-88-3", "108-88-3"), ["108-88-3"])

    def test_non_string_cas_is_coerced(self):
        """Parquet may hand back a numpy scalar rather than a str."""
        class Weird:
            def __str__(self):
                return "108-88-3"
        self.assertEqual(dn.dump_stem_candidates("toluene", Weird())[0], "108-88-3")

    def test_empty_name_and_cas_yields_nothing(self):
        self.assertEqual(dn.dump_stem_candidates("", None), [])


class TestFindDumpStem(unittest.TestCase):
    def test_prefers_cas_when_both_exist(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_dump(d, "108-88-3")
            _touch_dump(d, "toluene")
            self.assertEqual(dn.find_dump_stem(["108-88-3", "toluene"], d), "108-88-3")

    def test_falls_back_to_legacy_name(self):
        """A pre-rename dump must still be found."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_dump(d, "toluene")
            self.assertEqual(dn.find_dump_stem(["108-88-3", "toluene"], d), "toluene")

    def test_returns_none_when_absent(self):
        with TemporaryDirectory() as tmp:
            self.assertIsNone(dn.find_dump_stem(["108-88-3", "toluene"], Path(tmp)))

    def test_done_suffix_requires_a_finished_dump(self):
        """A dump killed mid-write has .dmp but no .done marker."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_dump(d, "108-88-3", suffixes=(".pkl", ".dmp"))  # truncated
            self.assertEqual(dn.find_dump_stem(["108-88-3"], d), "108-88-3")
            self.assertIsNone(dn.find_dump_stem(["108-88-3"], d, suffix=".done"))

    def test_missing_directory_is_not_an_error(self):
        with TemporaryDirectory() as tmp:
            self.assertIsNone(dn.find_dump_stem(["x"], Path(tmp) / "nope"))

    def test_finds_a_compressed_dump(self):
        """The mass-rebuild guard: a compressed dump is a dump that exists.

        If this regresses, --avoid-reprocessing reports the whole corpus missing and
        the next array rebuilds 1426 molecules from scratch.
        """
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_compressed_dump(d, "108-88-3")
            self.assertEqual(dn.find_dump_stem(["108-88-3"], d), "108-88-3")
            self.assertEqual(dn.find_dump_stem(["108-88-3"], d, suffix=".pkl"), "108-88-3")
            self.assertEqual(dn.find_dump_stem(["108-88-3"], d, suffix=".done"), "108-88-3")

    def test_finds_a_half_migrated_dump(self):
        """A run killed between the two files leaves one compressed, one not."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "108-88-3.pkl").write_bytes(b"legacy")
            with codec.open_write(d / "108-88-3.dmp") as handle:
                handle.write(b"compressed")
            self.assertEqual(dn.find_dump_stem(["108-88-3"], d, suffix=".pkl"), "108-88-3")
            self.assertEqual(dn.find_dump_stem(["108-88-3"], d, suffix=".dmp"), "108-88-3")


class TestDumpStems(unittest.TestCase):
    """Stem discovery, which Path.stem gets wrong for a compressed dump."""

    def test_collects_compressed_and_legacy_stems(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_compressed_dump(d, "108-88-3")
            _touch_dump(d, "toluene")
            self.assertEqual(dn.dump_stems(d), {"108-88-3", "toluene"})

    def test_stem_is_not_polluted_by_the_codec_suffix(self):
        """Path("x.pkl.zst").stem is "x.pkl" -- the bug this helper exists to avoid."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_compressed_dump(d, "108-88-3")
            self.assertNotIn("108-88-3.pkl", dn.dump_stems(d))

    def test_missing_directory_is_empty_not_an_error(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(dn.dump_stems(Path(tmp) / "nope"), set())


class TestDoneMarker(unittest.TestCase):
    def test_payload_round_trips(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            dn.write_done_marker(d, "108-88-3", dmp_bytes=111, pkl_bytes=222)
            payload = dn.read_done_marker(d, "108-88-3")
            self.assertEqual((payload["dmp_bytes"], payload["pkl_bytes"]), (111, 222))

    def test_legacy_zero_byte_marker_reads_as_no_payload(self):
        """Every pre-compression marker is empty; that must not read as 'incomplete'."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / f"108-88-3{dn.DONE_SUFFIX}").write_bytes(b"")
            self.assertIsNone(dn.read_done_marker(d, "108-88-3"))
            self.assertEqual(dn.find_dump_stem(["108-88-3"], d, suffix=".done"), "108-88-3")

    def test_uncompressed_bytes_come_from_the_marker(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_compressed_dump(d, "108-88-3")
            dn.write_done_marker(d, "108-88-3", dmp_bytes=5000, pkl_bytes=4000)
            self.assertEqual(dn.dump_uncompressed_bytes("108-88-3", d), (9000, "done"))

    def test_uncompressed_bytes_fall_back_to_stat_for_a_legacy_dump(self):
        """An unmigrated tree must report exactly the pre-compression number."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "toluene.pkl").write_bytes(b"x" * 300)
            (d / "toluene.dmp").write_bytes(b"y" * 700)
            (d / f"toluene{dn.DONE_SUFFIX}").write_bytes(b"")
            self.assertEqual(dn.dump_uncompressed_bytes("toluene", d), (1000, "stat"))


class TestResolveDumpStem(unittest.TestCase):
    """resolve_dump_stem with the store lookup stubbed, so no Parquet is needed."""

    def setUp(self):
        self._real = dn.get_cas_by_smiles
        self.addCleanup(setattr, dn, "get_cas_by_smiles", self._real)

    def _stub_cas(self, value):
        dn.get_cas_by_smiles = lambda smiles, parquet_dir: value

    def test_resolves_name_to_the_cas_named_dump(self):
        """The generated_fwd_dg.sh regression: --name toluene, dump is 108-88-3."""
        self._stub_cas("108-88-3")
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_dump(d, "108-88-3")
            self.assertEqual(
                dn.resolve_dump_stem("toluene", "CC1=CC=CC=C1", d, "/unused"),
                "108-88-3")

    def test_molecule_absent_from_the_store_still_resolves_by_name(self):
        """Decoys and non-NIST molecules have no CAS but do have dumps."""
        self._stub_cas(None)
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_dump(d, "decoy_XYZ")
            self.assertEqual(
                dn.resolve_dump_stem("decoy_XYZ", "CCO", d, "/unused"), "decoy_XYZ")

    def test_unreadable_store_degrades_to_the_name(self):
        """A missing Parquet store must not crash a run over legacy dumps."""
        def boom(smiles, parquet_dir):
            raise FileNotFoundError("no store")
        dn.get_cas_by_smiles = boom
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            _touch_dump(d, "toluene")
            self.assertEqual(
                dn.resolve_dump_stem("toluene", "CC1=CC=CC=C1", d, "/gone"), "toluene")

    def test_returns_none_when_nothing_is_on_disk(self):
        self._stub_cas("108-88-3")
        with TemporaryDirectory() as tmp:
            self.assertIsNone(
                dn.resolve_dump_stem("toluene", "CC1=CC=CC=C1", Path(tmp), "/unused"))


if __name__ == "__main__":
    unittest.main()
