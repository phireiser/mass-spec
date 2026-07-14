"""
Traversal and saturation checks extracted from rule_extention.
"""
import collections
from typing import List, Set, Optional, Iterable
import mod
from .compareability import ComparableVertex
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
# rebuilds collapse to one per distinct reactant set. A strong ref to the term
# graph list is retained alongside each entry so that the `id()` fallback (used
# only for graphs without a mod id, e.g. in tests) can never be aliased by a
# recycled id(). The index stores only primitive (id, stringLabel) keys -- NOT mod
# vertices -- so an entry no longer pins the string-mode graph copies alive for the
# whole process; those are freed once built (see `_build_traversal_index`) and the
# weakref `_graph_from_term_cache` lets them go.
#
# Bounded LRU: a molecule that keeps discovering new reactant sets (the ones that
# run for hours) cannot grow this cache without limit. Eviction only forces a
# recompute of a pure function -- never a different result. The cap is high enough
# that molecules which complete never evict, so their timing/output are unchanged;
# it only bounds pathological long runs.
_TRAVERSAL_INDEX_CACHE_CAP = 4096
_traversal_index_cache: "collections.OrderedDict" = collections.OrderedDict()


def clear_traversal_index_cache() -> None:
    """Drop memoised traversal indices (call between mod universes/tests)."""
    _traversal_index_cache.clear()


def _vk(v: "mod.Graph.Vertex") -> tuple:
    """Primitive identity key for a vertex: ``(id, stringLabel)``.

    Hash- and equality-identical to ``ComparableVertex(v)`` (which keys on exactly
    these two attrs), so it is a drop-in dict/set key -- but it holds no reference
    to the mod vertex, so caching these keys does not pin the string-mode graph the
    vertex belongs to.
    """
    return (v.id, v.stringLabel)


def _key_label(k: tuple) -> str:
    """Cleaned molecular label for a vertex key; equals ``mol_cleaned_label(v)``."""
    return mol_cleaned_label_str(k[1])


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
        _traversal_index_cache.move_to_end(key)
        return hit[0]
    built = [graph_from_term(g) for g in graphs_list]
    idx = _build_traversal_index(built, graphs_list)
    _traversal_index_cache[key] = (idx, graphs_list)
    if len(_traversal_index_cache) > _TRAVERSAL_INDEX_CACHE_CAP:
        _traversal_index_cache.popitem(last=False)
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

    # Work in primitive (id, stringLabel) key space -- identical hashing/equality to
    # the old ComparableVertex-keyed set, but the index and the visited-set no longer
    # hold mod vertices. The second returned value (previously the raw vertices) is
    # not consumed by any caller; it is returned as the visited keys for parity.
    start_keys = [_vk(v) for v in start_vertices]
    visited = set(start_keys)
    queue = collections.deque(start_keys)
    labels = [_key_label(k) for k in start_keys]
    keys_out = list(start_keys)
    visits = 0
    while queue:
        k = queue.popleft()
        for nk in neighbor_adj.get(k, ()):
            if nk not in visited:
                visited.add(nk)
                queue.append(nk)
                labels.append(_key_label(nk))
                keys_out.append(nk)
                visits += 1
                if max_visits is not None and visits >= max_visits:
                    _diag_inc("collect_bfs_cap")
                    _diag_log(f"[subgroup] collect_bfs cap hit: visits={visits}, cap={max_visits}")
                    queue.clear()
                    break
    return labels, keys_out


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
    # Store primitive (id, stringLabel) keys, not mod vertices: the values used to
    # be raw `e.target`/`e.source` vertices, which pinned the string-mode graph
    # copies alive in the cache for the whole process. A key tuple carries the same
    # identity (ComparableVertex hashes/compares on exactly these attrs) and the
    # same cleaned label (derivable from the stringLabel), so the traversal result
    # is unchanged while the string graphs become collectable once this returns.
    neighbor_adj: dict = {}
    for gg in built_graphs:
        for e in gg.edges:
            s = _vk(e.source)
            t = _vk(e.target)
            neighbor_adj.setdefault(s, []).append(t)
            neighbor_adj.setdefault(t, []).append(s)
    single_bond_map: dict = {}
    for g in term_graphs:
        for e in g.edges:
            s = _vk(e.source)
            t = _vk(e.target)
            if (s, t) in single_bond_map:  # first edge wins, like get_edge_between
                continue
            is_single = decode_edge_label(e.stringLabel) == '-'
            single_bond_map[(s, t)] = is_single
            single_bond_map[(t, s)] = is_single
    return neighbor_adj, single_bond_map


def _path_satisfies_branch_rule(
        neighbors_of, path: List[tuple],
        morphism_keys: Set[tuple],
        branch_ok_labels: Set[str]
        ) -> bool:
    path_set = set(path)
    for k in path:
        for nk in neighbors_of(k):
            if nk in path_set:
                continue
            if nk not in morphism_keys:
                continue
            if _key_label(nk) not in branch_ok_labels:
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
    morphism_keys = {_vk(x) for x in match.codomain.vertices}
    start_key = _vk(start_vertex)
    end_key = _vk(end_vertex)
    if start_key not in morphism_keys:
        return False
    if end_key not in morphism_keys:
        return False
    if mol_cleaned_label(start_vertex) not in allowed_labels:
        return False
    if mol_cleaned_label(end_vertex) not in allowed_labels:
        return False
    if start_key == end_key:
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

    def neighbors_of(k):
        return neighbor_adj.get(k, ())

    def is_single_bond(u, v):
        return single_bond_map.get((u, v), False)

    stack = collections.deque()
    stack.append((start_key, [start_key], {start_key}))
    expansions = 0
    while stack:
        node, path, path_set = stack.pop()
        for nk in neighbors_of(node):
            if nk in path_set:
                continue
            if _key_label(nk) != "C":
                continue
            if not is_single_bond(node, nk):
                continue
            new_path = path + [nk]
            if nk == end_key:
                if _path_satisfies_branch_rule(
                    neighbors_of,
                    new_path,
                    morphism_keys,
                    branch_ok_labels
                    ):
                    return True
            else:
                stack.append((nk, new_path, path_set | {nk}))
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
