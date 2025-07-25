"""for and back transformations from term mode to string mode"""
import collections
import mod

term_bond_from_bond_type = {
    mod.BondType.Invalid: "__error1",
    mod.BondType.Single: "p(0)",
    mod.BondType.Double: "p(p(0))",
    mod.BondType.Triple: "p(p(p(0)))",
    mod.BondType.Aromatic: "__error2"
}


def term_from_graph(g: mod.Graph):
    """
    convert a molecue in string mode into a molecule that can only be used in term mode
    """
    s = "graph [\n"
    for v in g.vertices:
        try:
            s += f'node [ id {v.id} label "a({v.atomId.symbol}, {v.charge}, {v.radical})" ]'
        except mod.libpymod.LogicError:
            s += f'node [ id {v.id} label "a(_A, {v.charge}, {v.radical})" ]'

    for e in g.edges:
        bond_type = term_bond_from_bond_type[e.bondType]
        s += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'
    s +="]\n"
    return mod.graphGMLString(s, name=g.name + ", term", add=False)


def decode_vertex_label(l: str) -> str:
    """
    takes a term - bracked expression and returns a compact string representaito no that atom
    """
    assert l.startswith("a(")
    assert l.endswith(")")
    l = l[2:-1].split(", ")
    lab = l[0]
    c = int(l[1])
    r = int(l[2])
    if c > 0:
        lab += "+" * abs(c)
    elif c < 0:
        lab += "-" * abs(c)
    if r > 0: # not elif otherwise vertex can't be charged radical
        lab += "." * r
    return lab


def decode_edge_label(l: str) -> str:
    """
    takes a term - bracked expression and returns a compact string representation no that bond
    """
    assert l.startswith("e(")
    assert l.endswith(")")
    l = l[2:-1]
    if l == "0":
        assert False
    elif l == "p(0)":
        bt = "-"
    elif l == "p(p(0))":
        bt = "="
    elif l == "p(p(p(0)))":
        bt = "#"
    else:
        raise ValueError(f"Can not convert edge term '{l}' to a molecule.")
    return bt


def graph_from_term(g: mod.Graph) -> mod.Graph:
    """
    takes a graph in of string mode and returns a graph for term mode
    """
    s = "graph [\n"
    for v in g.vertices:
        label = decode_vertex_label(v.stringLabel)
        s += f'node [ id {v.id} label "{label}" ]\n'
    for e in g.edges:
        edge_label = decode_edge_label(e.stringLabel)
        # I don't kown why I need to exchange target and source
        s += f'edge [ source {e.target.id} target {e.source.id} label "{edge_label}" ]\n'
    s += "]\n"
    return mod.graphGMLString(s, name= g.name.replace(", term", ""), add=False)


def term_from_rule(r: mod.Rule) -> mod.Rule:
    """
    takes a rule for term mode and returns a rule for string mode
    """
    left = ""
    right = ""
    context = ""

    g = r.left
    for v in g.vertices:
        try:
            left += f'node [ id {v.id} label "a({v.atomId.symbol}, {v.charge}, {v.radical})" ]'
        except mod.libpymod.LogicError:
            left += f'node [ id {v.id} label "a(_A, {v.charge}, {v.radical})" ]'

    for e in g.edges:
        bond_type = term_bond_from_bond_type[e.bondType]
        left += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'
    g = r.context
    for v in g.vertices:
        if hasattr(v, "atomId"):
            try:
                symbol = v.atomId.symbol
                context += f'node [ id {v.id} label "a({symbol}, {v.charge}, {v.radical})" ]'
            except mod.libpymod.LogicError:
                context += f'node [ id {v.id} label "a(_A, {v.charge}, {v.radical})" ]'
    for e in g.edges:
        if hasattr(v, "bondType"):
            bond_type = term_bond_from_bond_type[e.bondType]
            context += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'
    g = r.right
    for v in g.vertices:
        try:
            symbol = v.atomId.symbol
            right += f'node [ id {v.id} label "a({symbol}, {v.charge}, {v.radical})" ]'
        except mod.libpymod.LogicError:
            right += f'node [ id {v.id} label "a(_A, {v.charge}, {v.radical})" ]'
    for e in g.edges:
        bond_type = term_bond_from_bond_type[e.bondType]
        right += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'

    s = f"rule [\n\tleft [\n{left}\t]\n\tcontext [\n{context}\t]\n\tright [\n{right}\t]\n]\n"

    return mod.ruleGMLString(s, name=r.name + ", term", add=False)


def rule_from_term(r: mod.Rule) -> mod.Rule:
    """
    takes a rule in of string mode and returns a rule for term mode
    """

    left = ""
    right = ""

    for v in r.left.vertices:
        label = decode_vertex_label(v.stringLabel)
        left += f'node [ id {v.id} label "{label}" ]\n'
        #print("v", r.name, decode_vertex_label(v.stringLabel), v.stringLabel)
    for e in r.left.edges:
        label = decode_edge_label(e.stringLabel)
        left += f'edge [ source {e.source.id} target {e.target.id} label "{label}" ]\n'
    for v in r.right.vertices:
        label = decode_vertex_label(v.stringLabel)
        right += f'node [ id {v.id} label "{label}" ]\n'
    for e in r.right.edges:
        label = decode_edge_label(e.stringLabel)
        right += f'edge [ source {e.source.id} target {e.target.id} label "{label}" ]\n'

    s = f"rule [\n\tleft [\n{left}\t]\n\tright [\n{right}\t]\n]\n"
    return mod.ruleGMLString(s, name = r.name.replace(", term", ""), add=False)


def multiline_equal(s1: str, s2: str) -> bool:
    """
    Return True if s1 and s2 are identical, or if you can swap
    one pair of adjacent lines in s1 to get s2.
    """
    lines1 = s1.splitlines()
    lines2 = s2.splitlines()
    # Quick checks
    if s1 == s2:
        return True
    if len(lines1) != len(lines2):
        return False

    return collections.Counter(lines1) == collections.Counter(lines2)
