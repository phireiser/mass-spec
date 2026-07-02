import unittest
import types

from src.data_generation.utils.metrics import coverage_stats, dice_coefficient, overlap_coefficient
from src.data_generation.utils import ALK_NES_LABELS
from src.data_generation.utils import traversal
from src.data_generation.utils import compareability


class TestMetrics(unittest.TestCase):
    """Test cases for set similarity metrics."""
    def test_dice_and_overlap_coefficients_handle_basic_cases(self):
        self.assertEqual(dice_coefficient([1, 2, 3], [2, 3, 4]), 4 / 6)
        self.assertEqual(dice_coefficient([], []), 0.0)
        self.assertEqual(overlap_coefficient([1, 2, 3], [2, 3, 4]), 2 / 3)
        self.assertEqual(overlap_coefficient([], [1, 2]), 0.0)

    def test_coverage_stats_reports_expected_summary(self):
        stats = coverage_stats([10, 20, 20, 30], [20, 30, 40])

        self.assertEqual(stats["Dice"], 2 / 3)
        self.assertEqual(stats["TPR"], 2 / 3)
        self.assertEqual(stats["MØD masses"], [10, 20, 30])
        self.assertEqual(stats["Ref masses"], [20, 30, 40])
        self.assertEqual(stats["MØD support"], 3)
        self.assertEqual(stats["Ref support"], 3)


class TestSaturationPath(unittest.TestCase):
    class FakeVertex:
        def __init__(self, vid, label):
            self.id = vid
            self.stringLabel = label

    class FakeEdge:
        def __init__(self, source, target, string_label="e(p(0))"):
            self.source = source
            self.target = target
            self.stringLabel = string_label

    class FakeGraph:
        def __init__(self, vertices, edges):
            self.vertices = vertices
            self.edges = edges

    class FakeMatch:
        def __init__(self, vertices):
            self.codomain = types.SimpleNamespace(vertices=vertices)

    def setUp(self):
        self._orig_traversal_mod = traversal.mod
        self._orig_compareability_mod = compareability.mod
        traversal.mod = types.SimpleNamespace(Graph=types.SimpleNamespace(Vertex=self.FakeVertex))
        compareability.mod = traversal.mod
        self._orig_graph_from_term = traversal.graph_from_term
        traversal.graph_from_term = lambda graph: graph

    def tearDown(self):
        traversal.mod = self._orig_traversal_mod
        compareability.mod = self._orig_compareability_mod
        traversal.graph_from_term = self._orig_graph_from_term

    def _make_graph(self, branch_label):
        v1 = self.FakeVertex(1, "C")
        v2 = self.FakeVertex(2, "C")
        v3 = self.FakeVertex(3, "C")
        branch = self.FakeVertex(4, branch_label)
        edges = [
            self.FakeEdge(v1, v2),
            self.FakeEdge(v2, v3),
            self.FakeEdge(v2, branch),
        ]
        graph = self.FakeGraph([v1, v2, v3, branch], edges)
        return graph, v1, v3

    def test_saturated_path_accepts_allowed_branch_labels(self):
        graph, start, end = self._make_graph("H")
        match = self.FakeMatch(graph.vertices)

        result = traversal.saturated_path(
            graph=[graph],
            start_vertex=start,
            end_vertex=end,
            allowed_labels={"C"},
            match=match,
            branch_ok_label=("H",),
        )

        self.assertTrue(result)

    def test_saturated_path_rejects_disallowed_branch_labels(self):
        graph, start, end = self._make_graph("O")
        match = self.FakeMatch(graph.vertices)

        result = traversal.saturated_path(
            graph=[graph],
            start_vertex=start,
            end_vertex=end,
            allowed_labels={"C"},
            match=match,
            branch_ok_label=("H",),
        )

        self.assertFalse(result)


class TestAlkylGroup(unittest.TestCase):
    class FakeVertex:
        def __init__(self, vid, label):
            self.id = vid
            self.stringLabel = label

    class FakeEdge:
        def __init__(self, source, target, string_label="e(p(0))"):
            self.source = source
            self.target = target
            self.stringLabel = string_label

    class FakeGraph:
        def __init__(self, vertices, edges):
            self.vertices = vertices
            self.edges = edges

    class FakeMatch:
        def __init__(self, vertices):
            self.domain = types.SimpleNamespace(vertices=vertices)

    def setUp(self):
        self._orig_traversal_mod = traversal.mod
        self._orig_compareability_mod = compareability.mod
        traversal.mod = types.SimpleNamespace(Graph=types.SimpleNamespace(Vertex=self.FakeVertex))
        compareability.mod = traversal.mod
        self._orig_graph_from_term = traversal.graph_from_term
        traversal.graph_from_term = lambda graph: graph

    def tearDown(self):
        traversal.mod = self._orig_traversal_mod
        compareability.mod = self._orig_compareability_mod
        traversal.graph_from_term = self._orig_graph_from_term

    def _make_graph(self, tail_label):
        v1 = self.FakeVertex(1, "C")
        v2 = self.FakeVertex(2, "C")
        tail = self.FakeVertex(3, tail_label)
        edges = [
            self.FakeEdge(v1, v2),
            self.FakeEdge(v2, tail),
        ]
        graph = self.FakeGraph([v1, v2, tail], edges)
        return graph, v1

    def test_alkyl_group_labels_stay_within_alkyl_atom_set(self):
        graph, start = self._make_graph("H")
        match = self.FakeMatch([start])

        neighbor_labels, _ = traversal.collect_bfs(
            graphs=[graph],
            start_vertices=[start],
            match=match,
        )

        self.assertTrue(set(neighbor_labels).issubset(set(ALK_NES_LABELS)))

    def test_alkyl_group_rejects_non_alkyl_labels(self):
        graph, start = self._make_graph("O")
        match = self.FakeMatch([start])

        neighbor_labels, _ = traversal.collect_bfs(
            graphs=[graph],
            start_vertices=[start],
            match=match,
        )

        self.assertFalse(set(neighbor_labels).issubset(set(ALK_NES_LABELS)))


if __name__ == "__main__":
    unittest.main()
