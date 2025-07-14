def getRule2MoleculeMap(derivation, graphs, labelSettings):
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

    return m.match


def vertexById(g, vid):
    return next(v for v in g.vertices if v.id == vid)


def mol_neighbors(g: "mod.Graph", v: "mod.Vertex") -> Iterable["mod.Vertex"]:
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

def mol_cleaned_label(v: "mod.Vertex") -> str:
    """Return the vertex label stripped of ``+`` and ``.`` characters."""

    strlab = getattr(v, "stringLabel", "")

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
    graphs: "mod.Graph",
    start_vertices: Iterable["mod.Vertex"],
    match,
) -> Tuple[List[str], List["mod.Vertex"]]:
    """Breadth-first traversal over a :class:`mod.Graph`.

    The function walks the full molecular graph starting from
    *start_vertices*.  During the walk it *records* the cleaned labels
    (``+``/``.`` removed) **only for vertices that lie on the molecule
    side of the *match* morphism**.

    Parameters
    ----------
    graphs : List[mod.Graph]
    start_vertices : iterable of mod.Vertex
        Initial BFS frontier.
    match : dict
        Mapping *rule-vertex -> molecule-vertex* produced by
        :class:`DGVertexMapper`.  The *values* identify which vertices
        are “in morphism”.

    Returns
    -------
    labels : list[str]
        Cleaned labels for *morphism* vertices encountered in discovery
        order.
    vertices : list[mod.Vertex]
        The corresponding molecule vertices, parallel to *labels*.
    """
    graph = [] 
    for g in graphs:
        graph.append(graphFromTerm(g))
    
    #print(start_vertices)
    
    # exclude start vertices from morphism vertices as they are part of subgroup
    morphism_vertices: Set[mod.Graph.Vertex] = set([ x for x in match.domain.vertices]) - set(start_vertices) 

    visited: Set[mod.Graph.Vertex] = morphism_vertices
    queue: deque[mod.Graph.Vertex] = deque(start_vertices)

    labels: List[str] = [mol_cleaned_label(v) for v in start_vertices]
    vertices: List[mod.Graph.Vertex] = list(start_vertices)
    while queue:
        v = queue.popleft()
        #print("v", v.stringLabel, v.id)
        for vertex in mol_neighbors(graph, v):
            #print("vn", vertex) #not getting here but should have neigbours
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
    branch_ok_label: str,
) -> bool:
    """
    Return *True* iff every *side branch* off *path* (within the
    morphism) ends at a vertex whose cleaned label equals
    *branch_ok_label*.
    """

    path_set = set(path)

    for v in path:
        for neighbor in mol_neighbors(graph, v):
            if neighbor in path_set:                       # on the path -> ignore
                continue
            if neighbor not in morphism_vertices:          # outside morphism -> ignore
                continue
            if mol_cleaned_label(neighbor) != branch_ok_label: #mol added 
                return False
    return True

def get_edge_between(graph: mod.Graph, u: mod.Graph.Vertex, v: mod.Graph.Vertex) -> mod.Graph.Edge | None:

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


def _is_single_bond(graph: mod.Graph, u: mod.Graph.Vertex, v: mod.Graph.Vertex) -> bool:
    """
    Return True iff edge between *u* and *v* is a single bond.
    """
    edge = get_edge_between(graph, u, v)
    print("single", edge)

    if edge is None:                          # no edge at all
        return False

    return edge.bondType == mod.BondType.Single

def saturatedPath(
    graph: mod.Graph,
    start_vertex: mod.Graph.Vertex,
    end_vertex: mod.Graph.Vertex,
    allowed_labels: Set[str],
    match,
    branch_ok_label: str = "H",
) -> bool:
    """Return *True* iff there exists a simple path from *start_vertex* to
    *end_vertex* such that

    * every vertex on the path is **inside** the molecule-side of
      *match* **and** its cleaned label is in *allowed_labels*;
    * the path has **no side branches** inside the morphism except to
      vertices whose cleaned label equals *branch_ok_label*.

    The ``blocked_nodes`` parameter of the original networkx version has
    been removed; the morphism itself implicitly defines the allowed
    subgraph.
    """

    morphism_vertices: Set["mod.Vertex"] = set(match.codomain.vertices)

    print("start", (start_vertex.id, start_vertex.stringLabel))
    print("end", (end_vertex.id, end_vertex.stringLabel))
    #print("mor v", [(m.id, m.stringLabel, m) for m in morphism_vertices])

    comp_morphism_vertices = ComparableVertexList(morphism_vertices)

    # Early exits
    if ComparableVertex(start_vertex) not in comp_morphism_vertices:
        print("ee", "start not mapped")
        return False
    if ComparableVertex(end_vertex) not in comp_morphism_vertices:
        print("ee", "end not mapped")
        return False
    if mol_cleaned_label(start_vertex) not in allowed_labels:
        print("ee", "start label bad")
        return False
    if mol_cleaned_label(end_vertex) not in allowed_labels:
        print("ee", "end label bad")
        return False
    if start_vertex == end_vertex:
        print("ee", "start equals end")
        return True  # covered by the checks above

    stack: deque[Tuple["mod.Vertex", List["mod.Vertex"]]] = deque()
    stack.append((start_vertex, [start_vertex]))

    while stack:
        node, path = stack.pop()
        for vertex in mol_neighbors(graph, node):
            print("vn", vertex.id, vertex.stringLabel)
            #if ComparableVertex(vertex) not in comp_morphism_vertices:          # stay inside morphism
            #   continue
            #if ComparableVertex(vertex) in ComparableVertexList(path):          # checks if the current vertex is already in the path
            #    continue
            if mol_cleaned_label(vertex) != "C":                                # label filter
                continue
            if not _is_single_bond(graph, node, vertex):                        # single bonds only
                continue

            new_path = path + [vertex]

            if CompareableVertex(vertex) == CompareableVertex(end_vertex):
                print("hallo")
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

