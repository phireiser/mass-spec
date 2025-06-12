import requests, json, warnings, re, itertools, sys
import networkx as nx

from collections import deque
from typing import List, Tuple, Iterable, Set, Hashable, Dict, Optional

sys.setrecursionlimit(5000)

alkyl_stump_dfs = [ # _R_#
    "[C]{a1}([H]{a2})([H]{a3})([H]{a4})",
    "[C]{a1}([H]{a2})([H]{a3})([C]{a4})",
    "[C]{a1}([H]{a2})([C]{a3})([C]{a4})",
    "[C]{a1}([C]{a2})([C]{a3})([C]{a4})",
    "[C]{a1}",
]

saturation_stump_dfs = [ # _X_#
    "[C]{a1}",
    "[C]{a1}[C]{a2}",
    "[C]{a1}[C]{a2}[C]{a3}",
    "[C]{a1}[C]{a2}[C]{a3}[C]{a4}",
    "[C]{a1}[C]{a2}[C]{a3}[C]{a4}[C]{a5}",
    "[C]{a1}[C]{a2}[C]{a3}[C]{a4}[C]{a5}[C]{a6}",
]

# all Elements until Z = 99 as phase Z > 99 is unkown & origin = syntheic
# TODO ? functional group containing heteroAtom, this is only heteroAtoms itself


def addConstraints(rule, conStringGML):
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = ruleGMLString(gmlstr[:-1] + conStringGML + gmlstr[-1], name)
    return rule


def convert2MoelRule(tupel):
    if isinstance(tupel, tuple):
        tupel = [tupel]
    return [ Rule.fromDFS(rule, name= name) for rule, name in tupel ]


def flatten_list(nested_list):
    """
    Flattens a nested list into a single list.
    
    :param nested_list: A list which may contain other lists
    :return: A flattened list
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def printRules(inRules):
    post.summarySection("Rule(s)")
    p = GraphPrinter()
    p.setReactionDefault()
    p.withIndex = True
    inRules = flatten_list(inRules)
    for r in inRules:
            r.print(p)


def printGraphs(inGraphs):
    post.summarySection("Molecule(s)")
    p = GraphPrinter()
    p.setMolDefault()
    #p.withIndex = True
    for m in inGraphs:
            m.print(p)


def printGrammar(inGraphs = inputGraphs, inRules = inputRules):
    printGraphs(inGraphs)
    printRules(inRules)


def labelConstraints_gml(input_rules, rpl_dict):
    """
    every underscore single Letter combination should be replaced according to rpl dict

    :param rule: a moel ruel or list of them
    :param rpl_dict: dictionary with key as lable to be replaced and a string or list of strings to substitue with
    :return: list of rules
    """
    if not isinstance(input_rules, list):
        input_rules = [input_rules]
    return_rules = list()
    for rule in input_rules:
        gmlString = rule.getGMLString()
        rules = list()
        for old_structure, new_structure in rpl_dict.items():
            if not isinstance(new_structure, list):
                new_structure = list(new_structure)
            for new_i in new_structure:
                alteredStringObj = gmlString.replace(old_structure, new_i)
                alteredRuleObj = Rule.fromGMLString(alteredStringObj)
                alteredRuleObj.name = rule.name + " " + new_i
                rules.append(alteredRuleObj)
        return_rules.append(rules) 
    return return_rules


def labelConstraints_dfs(input_rules, to_replace, replacements):
    """
    every underscore single Letter combination should be replaced according to rpl dict

    :param rule: a moel ruel as a DFS string or list of them
    :param rpl_dict: dictionary with key as lable to be replaced and a string or list of strings to substitue with
    :return: list of rules
    """

    #https://www.mathsisfun.com/combinatorics/combinations-permutations.html
    #https://docs.python.org/3/library/itertools.html
    return_rules = list()

    if not isinstance(input_rules, list):
        input_rules = [input_rules]
    for rule, name in input_rules:
        for combo in itertools.product(replacements, repeat=len(to_replace)):
            new_rule = rule
            for target, repl in zip(to_replace, combo):
                
                # determine atom node id start from max occuring id and build it
                nums = [int(n) for n in re.findall(r'\d+', new_rule)]
                max_node_id = max(nums)
                values = {
                            'a1': max_node_id + 1, 'a2': max_node_id + 2, 'a3': max_node_id + 3, 'a4': max_node_id + 4, 
                            'a5': max_node_id + 5, 'a6': max_node_id + 6,}
                repl = repl.format(**values)

                for radIon in [ "", "+", ".", "+.", ".+"]:
                    for i in range(1, max_node_id+1):
                        new_rule = new_rule.replace(
                            '[' + target + radIon + ']' + str(i), 
                            repl[:2] + radIon + repl[2:],
                            -1)
                            
            return_rules.append((new_rule, name))
    return return_rules


def pubChemSmilesLookUp(smiles):
    pug_pre_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
    url = pug_pre_url + smiles + '/cids/JSON'
    response = requests.get(url)
    response.raise_for_status()
    cids = response.json()['IdentifierList']['CID']
    cid = cids[0]
    if len(cids) > 1:
        raise RuntimeWarning("Expecting only one PubChem CID")
    return cid


def getSpectraFromInformationSection(information):

    fields_of_interest = [
        "Top 5 Peaks",
        "m/z Top Peak",
        "m/z 2nd Highest",
        "m/z 3rd Highest"
    ]

    mass_spec_data = list()
    extracted_value = list()

    for item in information:
        name = item.get("Name", "")
        reference_number = item.get("ReferenceNumber")
        value = item.get("Value", [])
        if name in fields_of_interest:
            if name in fields_of_interest[0]: # top 5 peaks
                for line in value["StringWithMarkup"]:
                    text = line["String"]
                    parts = text.split()
                    if len(parts) == 2:
                        try:
                            mz = float(parts[0])
                            intensity = float(parts[1])
                            extracted_value.append((mz, intensity))
                        except ValueError:
                            raise RuntimeWarning("not a float")
                            pass
                mass_spec_data.append({reference_number: extracted_value})
                extracted_value = list()
            elif name in fields_of_interest[1:]: # top 3
                number_list = value.get("Number", [])
                if len(number_list) == 1:
                    mz_value = float(number_list[0])
                    # use arbitrary intensity = 1.0
                    extracted_value.append((mz_value, 1.0))
                    if name in fields_of_interest[3]:
                        mass_spec_data.append({reference_number: extracted_value})
                        extracted_value = list()
    return mass_spec_data


def getInformationSectionFromPubChem(cid):

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Extract Sections related to Mass Spectrometry
    sections = data.get("Record", {}).get("Section", [])
    for section in sections:
        if section.get("TOCHeading") == "Spectral Information":
            for sub_section in section.get("Section", []):
                if sub_section.get("TOCHeading") == "Mass Spectrometry":
                    for subsub in sub_section.get("Section", []):
                        if subsub.get("TOCHeading") == "GC-MS":
                            return subsub["Information"]
                        else:
                            raise RuntimeError("no GC-MS in pubchem found for compound", cid)
    return None


def getSpectraFromPubChem(smiles):
    cid = pubChemSmilesLookUp(smiles)
    info = getInformationSectionFromPubChem(cid)
    spectra = getSpectraFromInformationSection(info)
    return spectra


def getParentRulesForGraph(derivationGraph, search_target_graph):
    parentRules = []
    visited = set()
    stack = [search_target_graph]

    while stack:
        current_graph = stack.pop()

        # Avoid reprocessing the same graph
        if id(current_graph) in visited:
            continue
        visited.add(id(current_graph))

        try:
            edges = derivationGraph.findVertex(current_graph).inEdges
        except:
            continue

        for edge in edges:
            try:
                for rule in edge.rules:
                    parentRules.append(rule.id)
            except:
                continue

            try:
                for source in edge.sources:
                    stack.append(source.graph)
            except mod.LogicError:
                print("mod logic Error")
                continue

    return parentRules


def getSpectraFRomMoelDerivationGraph(derivationGraph):
    spectra = list()
    sourceGraph = derivationGraph.graphDatabase[0]

    for graph in dg.createdGraphs:
            if graph.isMolecule:
                    if '+' in graph.getGMLString(): # only charged fragments can be detected
                            found = False # update spectra list if allready occuring

                            rules = set(getParentRulesForGraph(derivationGraph,graph))
                            
                            for i, (mass, occurence, old_rules) in enumerate(spectra):
                                    if abs(mass - graph.exactMass) < 1e-2:
                                            spectra[i] = (graph.exactMass, occurence + 1, old_rules.union(rules))
                                            found = True
                                            break
                            if not found: # add to spectra list if not occuring
                                    spectra.append((graph.exactMass, 1, rules))
            else:
                print(graph.getGMLString())
                raise RuntimeWarning("there are some graphs that are not molecules")
    return spectra


def dice_coefficient(a, b): # like F1 Socre
    set_a, set_b = set(a), set(b)
    return 2 * len(set_a & set_b) / (len(set_a) + len(set_b))


def overlap_coefficient(a, b):
    set_a, set_b = set(a), set(b)
    res = 0
    try:
        res = len(set_a & set_b) / min(len(set_a), len(set_b))
    except(ZeroDivisionError):
        pass
    return res


def GraphDFSWithIds2nx(repr_str: str) -> nx.Graph:
    """
    Convert an atom indexed graph string such as

        [C]1([C]2([C]3([C]4(=[O+.]5)[H]13)([H]11)[H]12)([H]9)[H]10)
        ([H]6)([H]7)[H]8

    into a networkx.Graph.  
    Nodes get attributes   element=...,  decoration=... (e.g. '+.' or '.'),
    and edges get attribute bond='-', '=', '#', …

    Parameters
    ----------
    repr_str : str
        Graph string in the custom format.

    Returns
    -------
    nx.Graph
        Undirected molecular graph.
    """

    # Tokenisation
    atom_pat = re.compile(r"\[([A-Z][a-z]?)([+\-\.]*)\](\d+)")
    tokens = []
    i = 0
    while i < len(repr_str):
        ch = repr_str[i]
        if ch == "[":
            m = atom_pat.match(repr_str, i)
            if not m:
                raise ValueError(f"Malformed atom at position {i}")
            elem, deco, idx = m.groups()
            tokens.append({"type": "atom",
                           "element": elem,
                           "decoration": deco,      # '+', '.', '+.', '' …
                           "index": int(idx)})
            i = m.end()
        elif ch in "= - #":                      # support more symbols if needed
            tokens.append({"type": "bond", "bond": ch})
            i += 1
        elif ch in "()":
            tokens.append({"type": "paren", "char": ch})
            i += 1
        else:                                   # digits after ) or formatting
            i += 1

    # Graph construction
    G = nx.Graph()

    branch_stack = []        # [(parent_atom, pending_bond), …]
    current_atom = None
    pending_bond = '-'       # default single bond

    for tok in tokens:
        t = tok["type"]

        if t == "atom":
            idx = tok["index"]
            G.add_node(idx,
                       element=tok["element"],
                       decoration=tok["decoration"])
            if current_atom is not None:
                G.add_edge(current_atom, idx, bond=pending_bond)
            current_atom = idx
            pending_bond = '-'          # reset to default after use

        elif t == "bond":
            pending_bond = tok["bond"]

        elif t == "paren":
            if tok["char"] == '(':
                branch_stack.append((current_atom, pending_bond))
            else:                       # ')'
                current_atom, pending_bond = branch_stack.pop()

    return G


def split_rule_dfs(rule: str) -> Tuple[List[str], List[str]]:
    """
    Split a ruleDFS of the form
        graphs_left >> graphs_right
    into two lists while ignoring dots that are inside any brackets.

    Returns
    -------
    left_graphs  : list[str]
    right_graphs : list[str]
    """
    # separate left & right
    if ">>" not in rule:
        raise ValueError("ruleDFS must contain '>>'")
    left_raw, right_raw = map(str.strip, rule.split(">>", 1))

    # helper: top-level dot splitter using ONE depth counter
    def split_side(side: str) -> List[str]:
        graphs, buf, depth = [], [], 0
        for ch in side:
            if ch in "[({":        # any opening bracket
                depth += 1
            elif ch in "])}":      # any closing bracket
                depth -= 1

            if ch == "." and depth == 0:   # separator only at top level
                graph = "".join(buf).strip()
                if graph:
                    graphs.append(graph)
                buf.clear()
            else:
                buf.append(ch)

        last = "".join(buf).strip()
        if last:
            graphs.append(last)
        return graphs

    return split_side(left_raw), split_side(right_raw)


def modGraph2netX(g_mod: mod.Graph):
    g_nx = nx.Graph()

    for v in g_mod.vertices:
        g_nx.add_node(
            v.id,
            label = v.stringLabel,
            charge = v.charge,
            radical= v.radical,
            isotope = v.isotope,
            atomId = v.atomId
        )

    for e in g_mod.edges:
        g_nx.add_edge(
            e.source.id, 
            e.target.id, 
            label=e.stringLabel
        )
    
    return g_nx


def printNxGraph(G):
    print("Nodes:")
    for node, data in G.nodes(data=True):
        label = data.get("label", node)
        print(f"{node}: {label}")

    # Print edges
    print("\nEdges:")
    for u, v in G.edges():
        print(f"{u} -- {v}")


def getRule2MoleculeMap(derivation, graphs):
    
    # instatiate a derivation graph to pass in the vertex map
    dg_new = DG(graphDatabase = graphs)

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
    """Yield neighbouring vertices of *v* in the *mod.Graph* *g*.

    The helper works for undirected molecular graphs where an edge is
    considered bidirectional.
    """

    for gg in g:
        for e in gg.edges:
            if e.source is v:
                yield e.target
            elif e.target is v:
                yield e.source

def mol_cleaned_label(v: "mod.Vertex") -> str:
    """Return the vertex label stripped of ``+`` and ``.`` characters."""
    return getattr(v, "stringLabel", "").replace("+", "").replace(".", "")

def collect_bfs(
    graph: "mod.Graph",
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
    graph : mod.Graph
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

    morphism_vertices: Set["mod.Vertex"] = set([ x for x in match.domain.vertices])

    visited: Set["mod.Vertex"] = set(start_vertices)
    queue: deque["mod.Vertex"] = deque(start_vertices)

    labels: List[str] = []
    vertices: List["mod.Vertex"] = []

    while queue:
        v = queue.popleft()
        for vertex in mol_neighbors(graph, v):
            if vertex in visited or vertex in morphism_vertices:
                continue
            else:
                visited.add(vertex)
                queue.append(vertex)
            
                labels.append(mol_cleaned_label(vertex))
                vertices.append(vertex)

    return labels, vertices

def _path_satisfies_branch_rule(
    graph: "mod.Graph",
    path: List["mod.Vertex"],
    morphism_vertices: Set["mod.Vertex"],
    branch_ok_label: str,
) -> bool:
    """Return *True* iff every *side branch* off *path* (within the
    morphism) ends at a vertex whose cleaned label equals
    *branch_ok_label*.
    """

    path_set = set(path)

    for v in path:
        for nbr in _neighbors(graph, v):
            if nbr in path_set:                       # on the path → ignore
                continue
            if nbr not in morphism_vertices:          # outside morphism → ignore
                continue
            if _cleaned_label(nbr) != branch_ok_label:
                return False
    return True


def path_no_branches(
    graph: "mod.Graph",
    start_vertex: "mod.Vertex",
    end_vertex: "mod.Vertex",
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

    morphism_vertices: Set["mod.Vertex"] = set(match.domain.vertices)

    # Early exits -----------------------------------------------------------
    if start_vertex not in morphism_vertices or end_vertex not in morphism_vertices:
        return False
    if mol_cleaned_label(start_vertex) not in allowed_labels or mol_cleaned_label(end_vertex) not in allowed_labels:
        return False
    if start_vertex == end_vertex:
        return True  # covered by the checks above

    stack: deque[Tuple["mod.Vertex", List["mod.Vertex"]]] = deque()
    stack.append((start_vertex, [start_vertex]))

    while stack:
        node, path = stack.pop()

        for vertex in mol_neighbors(graph, node):
            if vertex not in morphism_vertices:                  # stay inside morphism
                continue
            if vertex in path:                                   # simple path requirement
                continue
            if mol_cleaned_label(vertex) not in allowed_labels:     # label filter
                continue

            new_path = path + [vertex]

            if vertex == end_vertex:
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