"""
rule extention helper functions
"""
import re

import collections
from typing import List, Tuple, Iterable, Set
import mod

from .compareability import ComparableVertex, ComparableVertexList
from .term_transfers import decode_vertex_label, graph_from_term, decode_edge_label


def get_rule_2_molecule_map(
    derivation: mod.Derivation,
    graphs: mod.Graph,
    label_settings: mod.LabelSettings
    ):# -> mod.VertexMapRuleLeftGraphUnionGraph:

    """
    see the positon where the rule gets applied
    """
    # instatiate a derivation graph to pass in the vertex map
    dg_new = mod.DG(graphDatabase = graphs, labelSettings = label_settings)

    with dg_new.build() as b:
        d = mod.Derivation()

        d.left = derivation.left
        d.rule = derivation.rule
        d.right = derivation.right
        b.addDerivation(d)

    e = next(edge for edge in dg_new.edges if derivation.rule in edge.rules)
    vms = mod.DGVertexMapper(e)
    m = next(iter(vms), None)
    if m is None:
        # DGVertexMapper yielded no matches
        return None
    return m.match

def transfer_positions_of_generalization_extention(
    generalization_extention: List[str],
    match#: mod.VertexMapRuleLeftGraphUnionGraph
    ) -> Tuple[
        List[mod.Graph.Vertex],
        List[Tuple[mod.Graph.Vertex, mod.Graph.Vertex]],
        List[mod.Graph.Vertex]
    ]:
    """
    convert the genearalization extentions 2 vertexes of the graph
    """

    alkyl_structures = re.findall(r'R(\d+)', generalization_extention)
    hetro_structures = re.findall(r'Y(\d+)', generalization_extention)
    saturated_structures = re.findall(r'S(\d+)-(\d+)', generalization_extention)

    # make it 0 based
    alkyl_structures = [int(x) - 1 for x in alkyl_structures]
    hetro_structures = [int(x) - 1 for x in hetro_structures]
    saturated_structures = [(int(x[0])-1, int(x[1])-1)  for x in saturated_structures]

    alkyl_pos_in_graph = [match[vertex_by_id(match.domain, x)] for x in alkyl_structures]
    alkyl_pos_in_graph = [match[vertex_by_id(match.domain, x)] for x in hetro_structures]
    saturated_pos_in_graph = [
        (match[vertex_by_id(match.domain, x[0])], match[vertex_by_id(match.domain, x[1])])
        for x in saturated_structures
        ]

    return alkyl_pos_in_graph, alkyl_pos_in_graph, saturated_pos_in_graph

def vertex_by_id(g: mod.Graph, vid: int) -> Iterable[mod.Graph.Vertex]:
    """
    get the all vertex from one graph that have a spesific vertex id
    """
    return next(v for v in g.vertices if v.id == vid)


def mol_neighbors(g: mod.Graph, v: mod.Graph.Vertex) -> Iterable[mod.Graph.Vertex]:
    """
    Yield neighbouring vertices of *v* in the *mod.Graph* *g*.
    """

    for gg in g:
        #print("gg", gg, g, v, v.id)
        for e in gg.edges:
            #print("nbr", e)
            if ComparableVertex(e.source) == ComparableVertex(v):
                #print("nbr", e.target, e.target.id, e.target.stringLabel)
                yield e.target
            elif ComparableVertex(e.target) == ComparableVertex(v):
                #print("nbr", e.source, e.source.id, e.source.stringLabel)
                yield e.source

def mol_cleaned_label(v: mod.Graph.Vertex) -> str:
    """
    Return the vertex label stripped of ``+`` and ``.`` characters.
    """

    strlab = getattr(v, "stringLabel", "")

    # regex for term mode detection
    # Regex explanation:
    # ^a\(             literal “a(” at start
    #   ([^"(),\s]+)   1st group: one or more chars except quotes, commas, parentheses or whitespace
    #   ,\s*           comma + optional space
    #   (-?\d+)        2nd group: an integer (optional minus, then digits)
    #   ,\s*           comma + optional space
    #   (-?\d+)        3rd group: another integer
    # \)$              literal “)” at end
    pattern = re.compile(r'^a\(([^"(),\s]+),\s*(-?\d+),\s*(-?\d+)\)$')

    if pattern.match(strlab):
        strlab = decode_vertex_label(strlab)

    return strlab.replace("+", "").replace("-", "").replace(".", "")

def collect_bfs(
    graphs: mod.Graph,
    start_vertices: Iterable[mod.Graph.Vertex],
    match,
    ) -> Tuple[List[str], List[mod.Graph.Vertex]]:

    """
    collects neighbor lables & and vertex object
    in a BFS manner unless covered by morphism
    """


    graph = []
    for g in graphs:
        graph.append(graph_from_term(g))


    # exclude start vertices from morphism vertices as they are part of subgroup
    morphism_vertices = set( x for x in match.domain.vertices) - set(start_vertices)

    visited = morphism_vertices
    queue = collections.deque(start_vertices)

    labels = [mol_cleaned_label(v) for v in start_vertices]
    vertices = list(start_vertices)
    while queue:
        v = queue.popleft()
        for vertex in mol_neighbors(graph, v):
            if vertex not in visited:
                visited.add(vertex)
                queue.append(vertex)
                labels.append(mol_cleaned_label(vertex))
                vertices.append(vertex)

    return labels, vertices

def _path_satisfies_branch_rule(
    graph: mod.Graph,
    path: List[mod.Graph.Vertex],
    morphism_vertices: Set[mod.Graph.Vertex],
    branch_ok_label: List[str],
    ) -> bool:

    """
    Return *True* iff every *side branch* off *path* (within the
    morphism) ends at a vertex whose cleaned label equals
    *branch_ok_label*.
    """

    path_set = set(path)
    #TODO do I need a Compareable Vertex here?
    for v in path:
        for neighbor in mol_neighbors(graph, v):
            if ComparableVertex(neighbor) in ComparableVertexList(path_set): # on given path -> ignore
                continue
            if ComparableVertex(neighbor) not in ComparableVertexList(morphism_vertices): # outside morphism -> ignore
                continue
            if mol_cleaned_label(neighbor) not in branch_ok_label: # is it an OK Label
                return False
    return True

def get_edge_between(
    graph: mod.Graph,
    u: mod.Graph.Vertex,
    v: mod.Graph.Vertex
    ) -> mod.Graph.Edge | None:
    """
    findes an edge between 2 points in a molecuel graph
    """
    if ComparableVertex(v) == ComparableVertex(u):
        return None

    for g in graph:
        for e in g.edges:
            if ComparableVertex(u) == e.source and ComparableVertex(v) == e.target:
                return e
            if ComparableVertex(v) == e.source and ComparableVertex(u) == e.target:
                return e
            if ComparableVertex(u) == e.target and ComparableVertex(v) == e.source:
                return e
            if ComparableVertex(v) == e.target and ComparableVertex(u) == e.source:
                return e
    return None


def _is_single_bond(
    graph: mod.Graph,
    u: mod.Graph.Vertex,
    v: mod.Graph.Vertex
    ) -> bool:

    """
    Return True iff edge between *u* and *v* is a single bond.
    """

    edge = get_edge_between(graph, u, v)

    if edge is None: # no edge at all
        return False

    return decode_edge_label(edge.stringLabel) == '-'

def saturated_path(
    graph: mod.Graph,
    start_vertex: mod.Graph.Vertex,
    end_vertex: mod.Graph.Vertex,
    allowed_labels: Set[str],
    match,#: mod.VertexMapRuleLeftGraphUnionGraph,
    branch_ok_label: str = "H",
    ) -> bool:

    """
    checks if there is path between start and end
    that is saturated
    """

    morphism_vertices = set(match.codomain.vertices)
    comp_morphism_vertices = ComparableVertexList(morphism_vertices)

    # Early exits
    if ComparableVertex(start_vertex) not in comp_morphism_vertices: # start not in map
        return False
    if ComparableVertex(end_vertex) not in comp_morphism_vertices: # end not in map
        return False
    if mol_cleaned_label(start_vertex) not in allowed_labels: # start label not good
        return False
    if mol_cleaned_label(end_vertex) not in allowed_labels: # end label not good
        return False
    if start_vertex == end_vertex: # start equals end
        return True

    stack = collections.deque()
    stack.append((start_vertex, [start_vertex]))

    while stack:
        node, path = stack.pop()
        for vertex in mol_neighbors(graph, node):

            #if ComparableVertex(vertex) not in comp_morphism_vertices:
                # stay inside morphism TODO: do I really need that check?
            #   continue
            if ComparableVertex(vertex) in ComparableVertexList(path):
                # checks if the current vertex is already in the path, loop prevention
                continue
            if mol_cleaned_label(vertex) != "C":
                # label filter
                continue
            if not _is_single_bond(graph, node, vertex):
                 # single bonds only
                continue

            new_path = path + [vertex]

            if ComparableVertex(vertex) == ComparableVertex(end_vertex):
                if _path_satisfies_branch_rule(
                    graph,
                    new_path,
                    morphism_vertices,
                    branch_ok_label,
                ):
                    return True
            else:
                stack.append((vertex, new_path))

    return False
