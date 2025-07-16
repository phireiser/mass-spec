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


def modGraph2netX(g_mod: mod.Graph) -> nx.Graph:
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


def printNxGraph(G: nx.Graph) -> None:
    print("Nodes:")
    for node, data in G.nodes(data=True):
        label = data.get("label", node)
        print(f"{node}: {label}")

    # Print edges
    print("\nEdges:")
    for u, v in G.edges():
        print(f"{u} -- {v}")