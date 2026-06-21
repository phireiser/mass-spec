"""
Traversal and saturation checks extracted from rule_extention.
"""
import collections
from typing import List, Set, Optional, Iterable
import mod
from .compareability import ComparableVertex, ComparableVertexList
from .term_transfers import graph_from_term, decode_edge_label
from .label_utils import mol_cleaned_label_str
from .diag import _diag_log, _diag_inc


def vertex_by_id(g: mod.Graph, vid: int) -> mod.Graph.Vertex:
    return next(v for v in g.vertices if v.id == vid)


def mol_neighbors(graphs: Iterable[mod.Graph], v: mod.Graph.Vertex) -> Iterable[mod.Graph.Vertex]:
    graph = [graph_from_term(g) for g in graphs]
    for gg in graph:
        for e in gg.edges:
            if ComparableVertex(e.source) == ComparableVertex(v):
                yield e.target
            elif ComparableVertex(e.target) == ComparableVertex(v):
                yield e.source


def mol_cleaned_label(v: mod.Graph.Vertex) -> str:
    return mol_cleaned_label_str(getattr(v, "stringLabel", ""))


def collect_bfs(
        graphs: Iterable[mod.Graph],
        start_vertices: Iterable[mod.Graph.Vertex],
        match: mod.DGVertexMapper.Result.match,
        max_visits: Optional[int] = None
        ):
    morphism_vertices = set(x for x in match.domain.vertices) - set(start_vertices)
    visited = set(morphism_vertices)
    queue = collections.deque(start_vertices)
    labels = [mol_cleaned_label(v) for v in start_vertices]
    vertices = list(start_vertices)
    visits = 0
    while queue:
        v = queue.popleft()
        for vertex in mol_neighbors(graphs, v):
            if vertex not in visited:
                visited.add(vertex)
                queue.append(vertex)
                labels.append(mol_cleaned_label(vertex))
                vertices.append(vertex)
                visits += 1
                if max_visits is not None and visits >= max_visits:
                    _diag_inc("collect_bfs_cap")
                    _diag_log(f"[subgroup] collect_bfs cap hit: visits={visits}, cap={max_visits}")
                    queue.clear()
                    break
    return labels, vertices


def get_edge_between(graphs: Iterable[mod.Graph], u: mod.Graph.Vertex, v: mod.Graph.Vertex) -> mod.Graph.Edge | None:
    if ComparableVertex(v) == ComparableVertex(u):
        return None
    for g in graphs:
        for e in g.edges:
            if ComparableVertex(u) == ComparableVertex(e.source) and ComparableVertex(v) == ComparableVertex(e.target):
                return e
            if ComparableVertex(v) == ComparableVertex(e.source) and ComparableVertex(u) == ComparableVertex(e.target):
                return e
            if ComparableVertex(u) == ComparableVertex(e.target) and ComparableVertex(v) == ComparableVertex(e.source):
                return e
            if ComparableVertex(v) == ComparableVertex(e.target) and ComparableVertex(u) == ComparableVertex(e.source):
                return e
    return None


def _is_single_bond(graphs: Iterable[mod.Graph], u: mod.Graph.Vertex, v: mod.Graph.Vertex) -> bool:
    edge = get_edge_between(graphs, u, v)
    if edge is None:
        return False
    return decode_edge_label(edge.stringLabel) == '-'


# Lower bound (total vertices across the reactant graphs) above which
# saturated_path precomputes a neighbor/single-bond index. Below it the search
# space is small enough that the per-call helpers are cheaper than the index, so
# its initialization is skipped.
SATURATED_PATH_INDEX_MIN_VERTICES = 20


def _graph_size(built_graphs: Iterable[mod.Graph]) -> int:
    return sum(1 for gg in built_graphs for _ in gg.vertices)


def _build_traversal_index(
        built_graphs: List[mod.Graph],
        term_graphs: Iterable[mod.Graph]
        ) -> tuple[dict, dict]:
    """Precompute, once per call, what the DFS would otherwise recompute per step.

    ``neighbor_adj`` mirrors :func:`mol_neighbors` (neighbors taken from the
    term-mode graphs) and ``single_bond_map`` mirrors :func:`_is_single_bond`
    (bond type decoded from the raw term graphs). An indexed traversal therefore
    yields the same result as the per-call helpers -- without rebuilding the
    graphs and rescanning every edge on each step, which is what made large
    molecules (e.g. fused steroid rings) churn until the job was killed.
    """
    neighbor_adj: dict = {}
    for gg in built_graphs:
        for e in gg.edges:
            cs = ComparableVertex(e.source)
            ct = ComparableVertex(e.target)
            neighbor_adj.setdefault(cs, []).append(e.target)
            neighbor_adj.setdefault(ct, []).append(e.source)
    single_bond_map: dict = {}
    for g in term_graphs:
        for e in g.edges:
            cs = ComparableVertex(e.source)
            ct = ComparableVertex(e.target)
            if (cs, ct) in single_bond_map:  # first edge wins, like get_edge_between
                continue
            is_single = decode_edge_label(e.stringLabel) == '-'
            single_bond_map[(cs, ct)] = is_single
            single_bond_map[(ct, cs)] = is_single
    return neighbor_adj, single_bond_map


def _path_satisfies_branch_rule(
        neighbors_of, path: List[mod.Graph.Vertex],
        comp_morphism: Set[ComparableVertex],
        branch_ok_labels: Set[str]
        ) -> bool:
    comp_path = {ComparableVertex(x) for x in path}
    for v in path:
        for neighbor in neighbors_of(v):
            cn = ComparableVertex(neighbor)
            if cn in comp_path:
                continue
            if cn not in comp_morphism:
                continue
            if mol_cleaned_label(neighbor) not in branch_ok_labels:
                return False
    return True


def saturated_path(
        graph: mod.Graph,
        start_vertex: mod.Graph.Vertex,
        end_vertex: mod.Graph.Vertex,
        allowed_labels: Set[str],
        match: mod.DGVertexMapper.Result.match,
        branch_ok_label: Optional[Iterable[str]] = ("H",),
        max_expansions: Optional[int] = None
        ) -> bool:
    morphism_vertices = set(match.codomain.vertices)
    comp_morphism_vertices = ComparableVertexList(morphism_vertices)
    if ComparableVertex(start_vertex) not in comp_morphism_vertices:
        return False
    if ComparableVertex(end_vertex) not in comp_morphism_vertices:
        return False
    if mol_cleaned_label(start_vertex) not in allowed_labels:
        return False
    if mol_cleaned_label(end_vertex) not in allowed_labels:
        return False
    if start_vertex == end_vertex:
        return True
    if isinstance(branch_ok_label, str):
        branch_ok_labels = {branch_ok_label}
    else:
        branch_ok_labels = set(branch_ok_label)

    # Build the term-mode graphs once instead of rebuilding them on every
    # neighbor lookup (the original hot path). For large molecules also
    # precompute a neighbor/single-bond index; for small ones fall back to the
    # per-call helpers and skip the index initialization.
    built = [graph_from_term(g) for g in graph]
    if _graph_size(built) >= SATURATED_PATH_INDEX_MIN_VERTICES:
        neighbor_adj, single_bond_map = _build_traversal_index(built, graph)

        def neighbors_of(v):
            return neighbor_adj.get(ComparableVertex(v), ())

        def is_single_bond(u, v):
            return single_bond_map.get((ComparableVertex(u), ComparableVertex(v)), False)
    else:
        def neighbors_of(v):
            return mol_neighbors(graph, v)

        def is_single_bond(u, v):
            return _is_single_bond(graph, u, v)

    comp_morphism = {ComparableVertex(x) for x in morphism_vertices}
    comp_end = ComparableVertex(end_vertex)

    stack = collections.deque()
    stack.append((start_vertex, [start_vertex], {ComparableVertex(start_vertex)}))
    expansions = 0
    while stack:
        node, path, path_set = stack.pop()
        for vertex in neighbors_of(node):
            cv = ComparableVertex(vertex)
            if cv in path_set:
                continue
            if mol_cleaned_label(vertex) != "C":
                continue
            if not is_single_bond(node, vertex):
                continue
            new_path = path + [vertex]
            if cv == comp_end:
                if _path_satisfies_branch_rule(neighbors_of, new_path, comp_morphism, branch_ok_labels):
                    return True
            else:
                stack.append((vertex, new_path, path_set | {cv}))
                expansions += 1
                # Safety guard against combinatorial blow-up: the index makes
                # each step cheap, but the number of simple paths is still
                # unbounded. Count the hit for the diag summary; the per-hit log
                # is intentionally omitted to avoid flooding job output.
                if max_expansions is not None and expansions >= max_expansions:
                    _diag_inc("saturated_path_cap")
                    return False
    return False


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "vertex_by_id",
    "mol_neighbors",
    "mol_cleaned_label",
    "collect_bfs",
    "get_edge_between",
    "saturated_path",
]
