import re
import mod
from typing import List, Tuple

def getRule2MoleculeMap(
    derivation: mod.Derivation, 
    graphs: mod.Graph, 
    labelSettings: mod.LabelSettings
    ):# -> mod.VertexMapRuleLeftGraphUnionGraph:
    # instatiate a derivation graph to pass in the vertex map
    dg_new = DG(graphDatabase = graphs, labelSettings = labelSettings)

    with dg_new.build() as b:
        d = Derivation()
        
        d.left = derivation.left
        d.rule = derivation.rule
        d.right = derivation.right
        b.addDerivation(d)
    
    e = next(edge for edge in dg_new.edges if derivation.rule in edge.rules)
    vms = DGVertexMapper(e)
    m = next(iter(vms), None)
    if m is None:
        # DGVertexMapper yielded no matches
        return None
    return m.match

def transferPositionsOfGeneralizationExtention(
    generalization_extention: List[str], 
    match#: mod.VertexMapRuleLeftGraphUnionGraph
    ) -> Tuple[
        List[mod.Graph.Vertex], 
        List[Tuple[mod.Graph.Vertex, mod.Graph.Vertex]], 
        List[mod.Graph.Vertex]
    ]:

    alkylStructures = re.findall(r'R(\d+)', generalization_extention)
    hetroStructures = re.findall(r'Y(\d+)', generalization_extention)
    saturatedStructures = re.findall(r'S(\d+)-(\d+)', generalization_extention)
    
    # make it 0 based
    alkylStructures = [int(x) - 1 for x in alkylStructures]
    hetroStructures = [int(x) - 1 for x in hetroStructures]
    saturatedStructures = [(int(x[0])-1, int(x[1])-1)  for x in saturatedStructures]

    alkylPosInGraph = [match[vertexById(match.domain, x)] for x in alkylStructures]
    hetroPosInGraph = [match[vertexById(match.domain, x)] for x in hetroStructures]
    saturatedPosInGraph = [
        (match[vertexById(match.domain, x[0])], match[vertexById(match.domain, x[1])]) 
        for x in saturatedStructures
        ]
    
    return alkylPosInGraph, hetroPosInGraph, saturatedPosInGraph

def vertexById(g: mod.Graph, vid: int) -> Iterable[mod.Graph.Vertex]:
    return next(v for v in g.vertices if v.id == vid)


def mol_neighbors(g: mod.Graph, v: mod.Graph.Vertex) -> Iterable[mod.Graph.Vertex]:
    """Yield neighbouring vertices of *v* in the *mod.Graph* *g*."""

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
    """Return the vertex label stripped of ``+`` and ``.`` characters."""

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
        strlab = decodeVertexLabel(strlab)
    
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
        graph.append(graphFromTerm(g))
    
    
    # exclude start vertices from morphism vertices as they are part of subgroup
    morphism_vertices: Set[mod.Graph.Vertex] = set([ x for x in match.domain.vertices]) - set(start_vertices) 

    visited: Set[mod.Graph.Vertex] = morphism_vertices
    queue: deque[mod.Graph.Vertex] = deque(start_vertices)

    labels: List[str] = [mol_cleaned_label(v) for v in start_vertices]
    vertices: List[mod.Graph.Vertex] = list(start_vertices)
    while queue:
        v = queue.popleft()
        for vertex in mol_neighbors(graph, v):
            if vertex in visited:
                continue
            else:
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

    return decodeEdgeLabel(edge.stringLabel) == '-'

def saturatedPath(
    graph: mod.Graph,
    start_vertex: mod.Graph.Vertex,
    end_vertex: mod.Graph.Vertex,
    allowed_labels: Set[str],
    match,#: mod.VertexMapRuleLeftGraphUnionGraph,
    branch_ok_label: str = "H",
    ) -> bool:

    """

    """

    morphism_vertices: Set[mod.Graph.Vertex] = set(match.codomain.vertices)
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

    stack: deque[Tuple[mod.Graph.Vertex, List[mod.Graph.Vertex]]] = deque()
    stack.append((start_vertex, [start_vertex]))

    while stack:
        node, path = stack.pop()
        for vertex in mol_neighbors(graph, node):

            #if ComparableVertex(vertex) not in comp_morphism_vertices:          # stay inside morphism TODO: do I really need that check?
            #   continue
            if ComparableVertex(vertex) in ComparableVertexList(path):          # checks if the current vertex is already in the path, loop prevention
               continue
            if mol_cleaned_label(vertex) != "C":                                # label filter
                continue
            if not _is_single_bond(graph, node, vertex):                        # single bonds only
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

