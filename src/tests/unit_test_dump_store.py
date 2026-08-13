"""Dump persistence round trip (src/data_generation/utils/file.py).

``DefaultDGStore`` had no test at all, which was tolerable while it was two lines of
``pickle.dump``. It now compresses, stages writes through a scratch directory and falls
back to legacy files on read, so the round trip needs pinning.

``mod`` is stubbed out (same pattern as ``unit_test_data_generation_utils``): what is
under test is the storage plumbing, not MOD, and a fake makes the destructive cases --
a load that raises, a half-migrated pair -- cheap to construct. The real MOD round trip
is covered by ``integration_test_dump_roundtrip``.
"""

import os
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.data_generation.utils import codec
from src.data_generation.utils import dump_naming as dn
from src.data_generation.utils import file as dump_file


class FakeGraph:
    """Stands in for a mod.Graph/mod.Rule: carries its GML string and nothing else."""

    def __init__(self, gml):
        self._gml = gml

    def getGMLString(self):
        return self._gml


class FakeDG:
    """A mod.DG whose dump writes known bytes and whose load reads them back."""

    payload = b"\xa5eedges" + b"\x01\x02\x03" * 500

    def __init__(self, graphs):
        self.graphDatabase = [FakeGraph(g) for g in graphs]

    def dump(self, path):
        Path(path).write_bytes(self.payload)
        return path


class LoadedDG:
    def __init__(self, graph_database, rule_database, data):
        self.graphDatabase = graph_database
        self.ruleDatabase = rule_database
        self.data = data


class DumpStoreCase(unittest.TestCase):
    """Installs the mod stub for the duration of each test."""

    def setUp(self):
        self._real_mod = dump_file.mod
        self.load_calls = []

        def fake_load(graphDatabase, ruleDatabase, f):
            # Record what mod was handed, and prove the file is readable at that moment.
            self.load_calls.append(Path(f))
            return LoadedDG(graphDatabase, ruleDatabase, Path(f).read_bytes())

        dump_file.mod = types.SimpleNamespace(
            DG=types.SimpleNamespace(load=fake_load),
            Graph=types.SimpleNamespace(fromGMLString=lambda gml: FakeGraph(gml)),
            Rule=types.SimpleNamespace(fromGMLString=lambda gml: FakeGraph(gml)),
        )
        self.addCleanup(self._restore_mod)

    def _restore_mod(self):
        dump_file.mod = self._real_mod

    def store_dump(self, directory, name="108-88-3", graphs=("graph [ node [ id 0 ] ]",)):
        dg = FakeDG(graphs)
        dump_file.dump_derivation_graph(
            dg=dg, rule_list=[FakeGraph("rule [ ]")], name=name,
            smiles="CC1=CC=CC=C1", path=directory)
        return dg


class TestDump(DumpStoreCase):
    def test_writes_a_compressed_pair_and_a_marker(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d)
            self.assertEqual(
                sorted(p.name for p in d.iterdir()),
                ["108-88-3.dmp.zst", "108-88-3.done", "108-88-3.pkl.zst"])

    def test_marker_carries_the_uncompressed_sizes(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d)
            payload = dn.read_done_marker(d, "108-88-3")
            self.assertEqual(payload["codec"], "zstd")
            self.assertEqual(payload["dmp_bytes"], len(FakeDG.payload))
            # The recorded size is the graph's, not the compressed file's.
            self.assertGreater(payload["dmp_bytes"],
                               (d / "108-88-3.dmp.zst").stat().st_size)

    def test_dump_is_complete_sees_the_marker(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d)
            self.assertTrue(dump_file.dump_is_complete("108-88-3", d))

    def test_no_scratch_or_part_files_survive(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d)
            self.assertEqual([], list(d.glob("*.part")))
            self.assertEqual([], list(d.glob("dg.dmp")))

    def test_rewriting_a_legacy_dump_removes_the_uncompressed_original(self):
        """Otherwise a rebuild would leave both forms and save nothing."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "108-88-3.dmp").write_bytes(b"legacy")
            (d / "108-88-3.pkl").write_bytes(b"legacy")
            self.store_dump(d)
            self.assertFalse((d / "108-88-3.dmp").exists())
            self.assertFalse((d / "108-88-3.pkl").exists())


class TestLoad(DumpStoreCase):
    def test_round_trip_returns_what_mod_wrote(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d, graphs=("graph [ node [ id 0 ] ]", "graph [ node [ id 1 ] ]"))
            loaded = dump_file.load_derivation_graph("108-88-3", d)
            self.assertEqual(loaded.data, FakeDG.payload)
            self.assertEqual([g.getGMLString() for g in loaded.graphDatabase],
                             ["graph [ node [ id 0 ] ]", "graph [ node [ id 1 ] ]"])

    def test_scratch_copy_is_removed_after_the_load(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d)
            dump_file.load_derivation_graph("108-88-3", d)
            self.assertEqual(len(self.load_calls), 1)
            self.assertFalse(self.load_calls[0].exists())

    def test_scratch_copy_is_removed_when_mod_raises(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d)
            seen = []

            def boom(graphDatabase, ruleDatabase, f):
                seen.append(Path(f))
                raise RuntimeError("LogicError from mod")

            dump_file.mod.DG.load = boom
            with self.assertRaises(RuntimeError):
                dump_file.load_derivation_graph("108-88-3", d)
            self.assertFalse(seen[0].exists())

    def test_reads_a_legacy_uncompressed_pair(self):
        """The unmigrated corpus keeps loading, with no copy into scratch."""
        import pickle
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "108-88-3.dmp").write_bytes(FakeDG.payload)
            with open(d / "108-88-3.pkl", "wb") as handle:
                pickle.dump(("CCO", ["graph [ ]"], ["rule [ ]"]), handle)
            (d / "108-88-3.done").write_bytes(b"")
            loaded = dump_file.load_derivation_graph("108-88-3", d)
            self.assertEqual(loaded.data, FakeDG.payload)
            # Handed the real file, not a scratch copy.
            self.assertEqual(self.load_calls[0], d / "108-88-3.dmp")

    def test_reads_a_half_migrated_pair(self):
        """Killed between the two files: compressed .dmp, legacy .pkl."""
        import pickle
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            with codec.open_write(d / "108-88-3.dmp") as handle:
                handle.write(FakeDG.payload)
            with open(d / "108-88-3.pkl", "wb") as handle:
                pickle.dump(("CCO", ["graph [ ]"], ["rule [ ]"]), handle)
            loaded = dump_file.load_derivation_graph("108-88-3", d)
            self.assertEqual(loaded.data, FakeDG.payload)

    def test_legacy_four_tuple_pickle_still_loads(self):
        import pickle
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "108-88-3.dmp").write_bytes(FakeDG.payload)
            with open(d / "108-88-3.pkl", "wb") as handle:
                pickle.dump(("CCO", ["graph [ ]"], ["rule [ ]"], {"spectrum": 1}), handle)
            self.assertEqual(
                dump_file.load_derivation_graph("108-88-3", d).data, FakeDG.payload)

    def test_dump_is_loadable_is_false_for_a_missing_dump(self):
        with TemporaryDirectory() as tmp:
            self.assertFalse(dump_file.dump_is_loadable("nope", Path(tmp)))


class TestCodecNone(DumpStoreCase):
    """The opt-out restores exactly the pre-compression on-disk format."""

    def setUp(self):
        super().setUp()
        previous = os.environ.get(codec.CODEC_ENV)
        os.environ[codec.CODEC_ENV] = "none"
        self.addCleanup(lambda: os.environ.pop(codec.CODEC_ENV, None)
                        if previous is None else os.environ.__setitem__(codec.CODEC_ENV, previous))

    def test_writes_plain_files_that_still_load(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.store_dump(d)
            self.assertEqual(sorted(p.name for p in d.iterdir()),
                             ["108-88-3.dmp", "108-88-3.done", "108-88-3.pkl"])
            self.assertEqual(dump_file.load_derivation_graph("108-88-3", d).data,
                             FakeDG.payload)


if __name__ == "__main__":
    unittest.main()
