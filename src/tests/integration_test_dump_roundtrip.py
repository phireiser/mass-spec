"""Integration test: a real MOD derivation graph survives a compressed round trip.

``unit_test_dump_store`` stubs ``mod`` out, so it proves the plumbing but not the thing
the whole design rests on: that ``mod.DG.load`` reads its file *eagerly*. Dumps are
compressed on disk, and ``DG.load`` only accepts a path, so loading decompresses into a
scratch directory and deletes it as soon as ``load`` returns. If MOD were instead lazy
about that file, everything would look fine until the first traversal.

This test therefore deletes the scratch copy and only then walks the graph the way
``machine_learning/main.py`` does -- vertices, ``findVertex``, ``outEdges``, edge rules
and targets -- and compares against the in-memory DG the dump came from.
"""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import mod

from src.data_generation import utils
from src.data_generation.utils import codec
from src.data_generation.utils import dump_naming as dn
from src.data_generation.rules import fragmentation, ionization
from src.data_generation.core import strategy


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/integration_test.sh)",
)
class TestDumpRoundTrip(unittest.TestCase):
    """Build a small real DG, dump it, load it back, compare."""

    STEM = "108-88-3"

    @classmethod
    def setUpClass(cls):
        mod.getConfig()
        mod.config.common.numThreads = 1

        molecule = mod.Graph.fromSMILES("Cc1ccccc1", "toluene")
        molecule_term = utils.term_from_graph(molecule)
        aoc = utils.all_occuring([molecule], utils.ALL_ATOMS)

        ls = mod.LabelSettings(mod.LabelType.Term, mod.LabelRelation.Specialisation)
        dg = mod.DG(graphDatabase=[molecule_term], labelSettings=ls)

        cls.ionization_terms = [utils.term_from_rule(r)
                                for r in utils.apply_constraints(ionization, aoc)]
        cls.fragmentation_terms = [utils.term_from_rule(r)
                                   for r in utils.apply_constraints(fragmentation, aoc)]

        dg.build().execute(strategy.make_fwd_strategy(
            derivation_graph=dg,
            universe=molecule_term,
            ionization=cls.ionization_terms,
            fragmentation=cls.fragmentation_terms,
            max_mass=molecule.exactMass,
        ))
        cls.dg = dg
        cls.expected_vertices = dg.numVertices
        cls.expected_edges = dg.numEdges

    def dump_into(self, directory):
        utils.dump_derivation_graph(
            dg=self.dg,
            rule_list=self.ionization_terms + self.fragmentation_terms,
            name=self.STEM, smiles="Cc1ccccc1", path=directory)

    def test_the_dump_is_compressed_on_disk(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.dump_into(d)
            self.assertTrue((d / f"{self.STEM}.dmp.zst").exists())
            self.assertTrue((d / f"{self.STEM}.pkl.zst").exists())
            self.assertFalse((d / f"{self.STEM}.dmp").exists())

    def test_compression_actually_happens(self):
        """Guards against the layer silently degrading to a copy.

        Deliberately a loose bound. Toluene's DG is ~60 KB and compresses ~3.9x; ratio
        climbs with size and the corpus mass is in the 100 MB+ dumps, where a full-tree
        measurement gave ~47x. So this asserts "compression is working", not a number --
        a tight bound here would only encode how small the test molecule is.
        """
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.dump_into(d)
            payload = dn.read_done_marker(d, self.STEM)
            raw = payload["dmp_bytes"] + payload["pkl_bytes"]
            stored = dn.dump_stored_bytes(self.STEM, d)
            self.assertGreater(raw / stored, 2,
                               f"only {raw / stored:.1f}x on a real dump ({raw} -> {stored})")

    def test_graph_survives_after_the_scratch_copy_is_gone(self):
        """The load-bearing assumption: DG.load is eager, so the temp file can go."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.dump_into(d)
            loaded = utils.load_derivation_graph(self.STEM, d)

            # materialize() has already removed its scratch directory by now; walking
            # the graph here is what would fail if MOD had kept the file open.
            self.assertEqual(loaded.numVertices, self.expected_vertices)
            self.assertEqual(loaded.numEdges, self.expected_edges)
            self.assertEqual(sum(1 for _ in loaded.vertices), self.expected_vertices)

            edges_walked = 0
            for vertex in loaded.vertices:
                found = loaded.findVertex(vertex.graph)
                self.assertIsNotNone(found)
                for edge in found.outEdges:
                    edges_walked += 1
                    self.assertGreater(len(list(edge.rules)) + len(list(edge.targets)), 0)
            self.assertGreater(edges_walked, 0)

    def test_no_scratch_file_is_left_behind(self):
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            scratch = Path(tmp) / "scratch"
            previous = os.environ.get(codec.SCRATCH_ENV)
            os.environ[codec.SCRATCH_ENV] = str(scratch)
            try:
                self.dump_into(d)
                utils.load_derivation_graph(self.STEM, d)
            finally:
                if previous is None:
                    os.environ.pop(codec.SCRATCH_ENV, None)
                else:
                    os.environ[codec.SCRATCH_ENV] = previous
            self.assertEqual([], list(scratch.iterdir()))

    def test_species_match_the_original(self):
        """The .pkl half: every graph comes back with the same GML."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.dump_into(d)
            loaded = utils.load_derivation_graph(self.STEM, d)
            self.assertEqual(len(loaded.graphDatabase), len(self.dg.graphDatabase))

    def test_pickle_only_fast_path_reads_the_compressed_dump(self):
        """spect_mol never touches the .dmp; it must still read the compressed .pkl."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.dump_into(d)
            spectra = utils.get_spectra_from_dump(self.STEM, d)
            self.assertGreater(len(spectra), 0)

    def test_avoid_reprocessing_sees_the_compressed_dump(self):
        """The mass-rebuild guard, against a real dump rather than a touched file."""
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.dump_into(d)
            self.assertTrue(utils.dump_is_complete(self.STEM, d))
            self.assertTrue(utils.dump_is_loadable(self.STEM, d))
            self.assertEqual(utils.find_dump_stem([self.STEM], d), self.STEM)


if __name__ == "__main__":
    unittest.main()
