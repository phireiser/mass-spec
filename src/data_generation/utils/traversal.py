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


def collect_bfs(graphs: Iterable[mod.Graph], start_vertices: Iterable[mod.Graph.Vertex], match: mod.DGVertexMapper.Result.match, max_visits: Optional[int] = None):
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


def _path_satisfies_branch_rule(graph: mod.Graph, path: List[mod.Graph.Vertex], morphism_vertices: Set[mod.Graph.Vertex], branch_ok_labels: Set[str]) -> bool:
    comp_path = {ComparableVertex(x) for x in path}
    comp_morphism = {ComparableVertex(x) for x in morphism_vertices}
    for v in path:
        for neighbor in mol_neighbors(graph, v):
            cn = ComparableVertex(neighbor)
            if cn in comp_path:
                continue
            if cn not in comp_morphism:
                continue
            if mol_cleaned_label(neighbor) not in branch_ok_labels:
                return False
    return True


def saturated_path(graph: mod.Graph, start_vertex: mod.Graph.Vertex, end_vertex: mod.Graph.Vertex, allowed_labels: Set[str], match: mod.DGVertexMapper.Result.match, branch_ok_label: Optional[Iterable[str]] = ("H",), max_expansions: Optional[int] = None) -> bool:
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
    stack = collections.deque()
    stack.append((start_vertex, [start_vertex]))
    expansions = 0
    while stack:
        node, path = stack.pop()
        for vertex in mol_neighbors(graph, node):
            if ComparableVertex(vertex) in ComparableVertexList(path):
                continue
            if mol_cleaned_label(vertex) != "C":
                continue
            if not _is_single_bond(graph, node, vertex):
                continue
            new_path = path + [vertex]
            if ComparableVertex(vertex) == ComparableVertex(end_vertex):
                if _path_satisfies_branch_rule(graph, new_path, morphism_vertices, branch_ok_labels):
                    return True
            else:
                stack.append((vertex, new_path))
                expansions += 1
                if max_expansions is not None and expansions >= max_expansions:
                    _diag_inc("saturated_path_cap")
                    _diag_log(f"[subgroup] saturated_path cap hit: expansions={expansions}, cap={max_expansions}")
                    return False
    return False
