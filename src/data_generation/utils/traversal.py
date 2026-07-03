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


# The BFS/DFS in `collect_bfs`/`saturated_path` rebuild the same molecular
# adjacency + single-bond index from scratch on every derivation (255k rebuilds
# on toluene). The index is a pure function of the input graphs, which come from
# `derivation.left` and are reused across every match and every derivation that
# shares a reactant. We memoise on the graphs' stable `mod.Graph.id`s so those
# rebuilds collapse to one per distinct reactant set. A strong ref to the graph
# list is retained alongside each entry so that the `id()` fallback (used only for
# graphs without a mod id, e.g. in tests) can never be aliased by a recycled id().
_traversal_index_cache: dict = {}


def clear_traversal_index_cache() -> None:
    """Drop memoised traversal indices (call between mod universes/tests)."""
    _traversal_index_cache.clear()


def _graphs_cache_key(graphs_list: List[mod.Graph]) -> tuple:
    key = []
    for g in graphs_list:
        gid = getattr(g, "id", None)
        key.append(gid if gid is not None else ("obj", id(g)))
    return tuple(key)


def build_traversal_index_cached(graphs: Iterable[mod.Graph]) -> tuple[dict, dict]:
    """Cached ``(neighbor_adj, single_bond_map)`` for a set of term-mode graphs.

    Returns the same shared, read-only dicts as :func:`_build_traversal_index`;
    callers must not mutate them.
    """
    graphs_list = list(graphs)
    key = _graphs_cache_key(graphs_list)
    hit = _traversal_index_cache.get(key)
    if hit is not None:
        return hit[0]
    built = [graph_from_term(g) for g in graphs_list]
    idx = _build_traversal_index(built, graphs_list)
    _traversal_index_cache[key] = (idx, graphs_list)
    return idx


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
    # The adjacency itself is memoised per graph set, so repeated calls on the same
    # reactant reuse it (see `build_traversal_index_cached`).
    neighbor_adj, _ = build_traversal_index_cached(graphs)

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
    cu, cv = ComparableVertex(u), ComparableVertex(v)
    if cu == cv:
        return None
    for g in graphs:
        for e in g.edges:
            cs = ComparableVertex(e.source)
            ct = ComparableVertex(e.target)
            if {cs, ct} == {cu, cv}:
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
    # The index is memoised per graph set so repeated calls on the same reactant
    # (across matches/derivations) reuse it (see `build_traversal_index_cached`).
    neighbor_adj, single_bond_map = build_traversal_index_cached(graph)

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
    "build_traversal_index_cached",
    "clear_traversal_index_cache",
]
