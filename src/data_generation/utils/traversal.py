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


def mol_neighbors(
        graphs: Iterable[mod.Graph],
        v: mod.Graph.Vertex
        ) -> Iterable[mod.Graph.Vertex]:
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
    # Convert the term graphs to string mode *once* and index their adjacency,
    # instead of rebuilding every graph inside `mol_neighbors` on every dequeue
    # (the old hot path: a single small molecule reconverted its graph hundreds
    # of thousands of times). `ComparableVertex` gives vertices a real, stable
    # hash and cross-build value equality -- raw mod vertices all hash to 0 and
    # compare unequal across rebuilt graphs, so the old `visited` set degenerated
    # to an O(n^2) scan that never actually deduplicated and churned until the
    # `max_visits` cap. With a proper visited-set the BFS now terminates once the
    # reachable component is covered, yielding the same set of neighbour labels.
    built = [graph_from_term(g) for g in graphs]
    neighbor_adj: dict = {}
    for gg in built:
        for e in gg.edges:
            neighbor_adj.setdefault(ComparableVertex(e.source), []).append(e.target)
            neighbor_adj.setdefault(ComparableVertex(e.target), []).append(e.source)

    start = list(start_vertices)
    visited = {ComparableVertex(v) for v in start}
    queue = collections.deque(start)
    labels = [mol_cleaned_label(v) for v in start]
    vertices = list(start)
    visits = 0
    while queue:
        v = queue.popleft()
        for vertex in neighbor_adj.get(ComparableVertex(v), ()):
            cv = ComparableVertex(vertex)
            if cv not in visited:
                visited.add(cv)
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


def get_edge_between(
        graphs: Iterable[mod.Graph],
        u: mod.Graph.Vertex,
        v: mod.Graph.Vertex
        ) -> mod.Graph.Edge | None:
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


def _build_traversal_index(
        built_graphs: List[mod.Graph],
        term_graphs: Iterable[mod.Graph]
        ) -> tuple[dict, dict]:
    """Precompute, once per call, what the DFS would otherwise recompute per step.

    ``neighbor_adj`` maps each vertex to its molecular neighbours (taken from the
    built graphs) and ``single_bond_map`` records, per vertex pair, whether the
    connecting bond is single (decoded from the raw term graphs, first edge
    winning). An indexed traversal therefore yields the same result as a per-step
    neighbour/bond scan -- without rebuilding the graphs and rescanning every edge
    on each step, which is what made large molecules (e.g. fused steroid rings)
    churn until the job was killed.
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

    # Build the term-mode graphs once and precompute a neighbor/single-bond
    # index, instead of rebuilding every graph and rescanning every edge on each
    # DFS step (the original hot path). Profiling showed the per-step fallback
    # dominated runtime even for small molecules, so the index is now always
    # used; `_build_traversal_index` is documented to yield identical results.
    built = [graph_from_term(g) for g in graph]
    neighbor_adj, single_bond_map = _build_traversal_index(built, graph)

    def neighbors_of(v):
        return neighbor_adj.get(ComparableVertex(v), ())

    def is_single_bond(u, v):
        return single_bond_map.get((ComparableVertex(u), ComparableVertex(v)), False)

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
                if _path_satisfies_branch_rule(
                    neighbors_of,
                    new_path,
                    comp_morphism,
                    branch_ok_labels
                    ):
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
