"""Transparent dump compression (src/data_generation/utils/codec.py).

The corpus is 45 GB of dumps that compress ~25x, but the compression layer sits under
``--avoid-reprocessing``, so the failure mode it has to be pinned against is not "the
bytes came back wrong" -- that would be loud. It is "a dump that exists stopped being
found", which is silent and would make the next SLURM array rebuild all 1426 molecules,
including the multi-hour ones, straight into the wall clock.

So the load-bearing cases here are the backward-compatibility ones: legacy uncompressed
files must still be found and read, and a half-migrated dump must work either way round.
"""

import os
import pickle
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.data_generation.utils import codec

# The real first bytes of a mod DG dump and a protocol-4 pickle, so the "this is not
# compressed" cases are tested against what is actually on disk rather than a stand-in.
RAW_DMP_MAGIC = b"\xa5eedges"
RAW_PKL_MAGIC = b"\x80\x04"


class CodecEnvMixin:
    """Restores DUMP_CODEC/DUMP_SCRATCH, which are read per call, not cached."""

    def set_codec(self, value):
        previous = os.environ.get(codec.CODEC_ENV)
        self.addCleanup(self._restore, codec.CODEC_ENV, previous)
        if value is None:
            os.environ.pop(codec.CODEC_ENV, None)
        else:
            os.environ[codec.CODEC_ENV] = value

    @staticmethod
    def _restore(key, previous):
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous


class TestCodecSelection(CodecEnvMixin, unittest.TestCase):
    def test_defaults_to_zstd(self):
        self.set_codec(None)
        self.assertEqual(codec.active_codec(), "zstd")
        self.assertEqual(codec.codec_suffix(), ".zst")

    def test_none_is_a_pass_through(self):
        self.set_codec("none")
        self.assertEqual(codec.codec_suffix(), "")
        self.assertEqual(codec.compressed_path(Path("/x/y.pkl")), Path("/x/y.pkl"))

    def test_unknown_codec_is_rejected_loudly(self):
        self.set_codec("rot13")
        with self.assertRaises(ValueError):
            codec.active_codec()


class TestRoundTrip(CodecEnvMixin, unittest.TestCase):
    def test_bytes_survive_a_round_trip(self):
        payload = b"graph [ node [ id 0 label \"a(C, 0, 0)\" ] ]" * 500
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            with codec.open_write(base) as handle:
                handle.write(payload)
            with codec.open_read(base) as handle:
                self.assertEqual(handle.read(), payload)

    def test_the_file_on_disk_is_actually_smaller(self):
        payload = b"a(C, 0, 0)" * 20000
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.pkl"
            with codec.open_write(base) as handle:
                handle.write(payload)
            stored = codec.resolve_read_path(base).stat().st_size
            self.assertLess(stored, len(payload) / 5)

    def test_pickle_streams_through_the_compressed_file(self):
        """The .pkl path never materialises an intermediate; it pickles into the stream."""
        data = ("CCO", ["graph [ node [ id 0 ] ]"] * 100, ["rule [ ]"])
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.pkl"
            with codec.open_write(base) as handle:
                pickle.dump(data, handle)
            with codec.open_read(base) as handle:
                self.assertEqual(pickle.load(handle), data)

    def test_compressed_file_carries_the_codec_suffix(self):
        self.set_codec("zstd")
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "108-88-3.pkl"
            with codec.open_write(base) as handle:
                handle.write(b"x")
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["108-88-3.pkl.zst"])

    def test_codec_none_writes_plain_bytes(self):
        self.set_codec("none")
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.pkl"
            with codec.open_write(base) as handle:
                handle.write(RAW_PKL_MAGIC)
            self.assertEqual(base.read_bytes(), RAW_PKL_MAGIC)
            with codec.open_read(base) as handle:
                self.assertEqual(handle.read(), RAW_PKL_MAGIC)


class TestLegacyCompatibility(CodecEnvMixin, unittest.TestCase):
    """The pre-compression corpus must stay readable. This is the mass-rebuild guard."""

    def test_reads_a_legacy_uncompressed_file(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            base.write_bytes(RAW_DMP_MAGIC)
            with codec.open_read(base) as handle:
                self.assertEqual(handle.read(), RAW_DMP_MAGIC)

    def test_exists_sees_a_legacy_file(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            base.write_bytes(RAW_DMP_MAGIC)
            self.assertTrue(codec.exists(base))

    def test_exists_sees_a_compressed_file(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            with codec.open_write(base) as handle:
                handle.write(RAW_DMP_MAGIC)
            self.assertTrue(codec.exists(base))

    def test_exists_is_false_when_nothing_is_there(self):
        with TemporaryDirectory() as tmp:
            self.assertFalse(codec.exists(Path(tmp) / "nope.dmp"))

    def test_compressed_wins_when_both_forms_exist(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            base.write_bytes(b"stale legacy")
            with codec.open_write(base) as handle:
                handle.write(b"fresh compressed")
            with codec.open_read(base) as handle:
                self.assertEqual(handle.read(), b"fresh compressed")

    def test_missing_file_names_what_it_tried(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError) as caught:
                codec.resolve_read_path(Path(tmp) / "gone.pkl")
            self.assertIn("gone.pkl.zst", str(caught.exception))


class TestAtomicity(CodecEnvMixin, unittest.TestCase):
    """A job killed at the wall limit must not leave a file that looks finished."""

    def test_nothing_is_left_behind_when_the_writer_raises(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.pkl"
            with self.assertRaises(RuntimeError):
                with codec.open_write(base) as handle:
                    handle.write(b"partial")
                    raise RuntimeError("killed mid-write")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_an_existing_file_survives_a_failed_rewrite(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.pkl"
            with codec.open_write(base) as handle:
                handle.write(b"good")
            with self.assertRaises(RuntimeError):
                with codec.open_write(base) as handle:
                    handle.write(b"bad")
                    raise RuntimeError("killed mid-write")
            with codec.open_read(base) as handle:
                self.assertEqual(handle.read(), b"good")

    def test_no_part_file_survives_a_successful_write(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.pkl"
            with codec.open_write(base) as handle:
                handle.write(b"done")
            self.assertEqual([], list(Path(tmp).glob("*.part")))


class TestFileHelpers(CodecEnvMixin, unittest.TestCase):
    def test_compress_file_reports_the_uncompressed_size(self):
        payload = b"x" * 5000
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.bin"
            src.write_bytes(payload)
            base = Path(tmp) / "dest.dmp"
            self.assertEqual(codec.compress_file(src, base), len(payload))
            with codec.open_read(base) as handle:
                self.assertEqual(handle.read(), payload)

    def test_decompress_to_restores_the_original_bytes(self):
        payload = RAW_DMP_MAGIC + b"\x00\x01\x02" * 3000
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            with codec.open_write(base) as handle:
                handle.write(payload)
            out = Path(tmp) / "restored.dmp"
            self.assertEqual(codec.decompress_to(base, out), len(payload))
            self.assertEqual(out.read_bytes(), payload)

    def test_drop_stale_variants_removes_the_legacy_twin(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            base.write_bytes(b"legacy")
            with codec.open_write(base) as handle:
                handle.write(b"compressed")
            codec.drop_stale_variants(base)
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["x.dmp.zst"])


class TestMaterialize(CodecEnvMixin, unittest.TestCase):
    """mod.DG.load needs a real path; this is how it gets one."""

    def test_legacy_file_is_yielded_without_copying(self):
        """Reading the unmigrated corpus must cost exactly what it costs today."""
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            base.write_bytes(RAW_DMP_MAGIC)
            with codec.materialize(base) as path:
                self.assertEqual(path, base)

    def test_compressed_file_is_expanded_then_cleaned_up(self):
        payload = RAW_DMP_MAGIC + b"body" * 1000
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            with codec.open_write(base) as handle:
                handle.write(payload)
            with codec.materialize(base) as path:
                self.assertNotEqual(path, base)
                self.assertEqual(path.read_bytes(), payload)
                escaped = path
            self.assertFalse(escaped.exists())

    def test_scratch_is_cleaned_up_when_the_body_raises(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp) / "x.dmp"
            with codec.open_write(base) as handle:
                handle.write(b"body")
            escaped = None
            with self.assertRaises(RuntimeError):
                with codec.materialize(base) as path:
                    escaped = path
                    raise RuntimeError("DG.load blew up")
            self.assertFalse(escaped.exists())

    def test_scratch_honours_the_override(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "scratch"
            previous = os.environ.get(codec.SCRATCH_ENV)
            os.environ[codec.SCRATCH_ENV] = str(root)
            self.addCleanup(self._restore, codec.SCRATCH_ENV, previous)
            with codec.scratch_dir() as path:
                self.assertEqual(path.parent, root)


if __name__ == "__main__":
    unittest.main()
