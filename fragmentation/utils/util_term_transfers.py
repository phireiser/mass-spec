import mod

termBondFromBondType = {
    mod.BondType.Invalid: "__error1",
    mod.BondType.Single: "p(0)",
    mod.BondType.Double: "p(p(0))",
    mod.BondType.Triple: "p(p(p(0)))",
    mod.BondType.Aromatic: "__error2"
}

#===
def termFromGraph(g: mod.Graph):
    s = "graph [\n"
    for v in g.vertices:
        try:
            s += 'node [ id %d label "a(%s, %d, %d)" ]' % (
                v.id, 
                v.atomId.symbol, 
                v.charge, 
                v.radical,
            )
        except mod.libpymod.LogicError as e:
            s += 'node [ id %d label "a(_A, %d, %d)" ]' % (v.id, v.charge, v.radical)

    for e in g.edges:
        s += 'edge [ source %d target %d label "e(%s)" ]' % (
            e.source.id,  
            e.target.id,
            termBondFromBondType[e.bondType]
        )
    s +="]\n"
    return mod.graphGMLString(s, name=g.name + ", term", add=False)

#===
def decodeVertexLabel(l: str) -> str:
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

#===
def decodeEdgeLabel(l: str) -> str:
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
        raise ValueError("Can not convert edge term '%s' to a molecule." % l)
    return bt

#===
def graphFromTerm(g: str) -> str:
    s = "graph [\n"
    for v in g.vertices:
        s += 'node [ id %d label "%s" ]\n' % (
            v.id, 
            decodeVertexLabel(v.stringLabel)
        )
    for e in g.edges:
        s += 'edge [ source %d target %d label "%s" ]\n' % (
            e.target.id,  e.source.id, # I don't kown why I need to exchange them
            decodeEdgeLabel(e.stringLabel)
        )
    s += "]\n"
    return mod.graphGMLString(s, name= g.name.replace(", term", ""), add=False)


#===
def termFromRule(r: mod.Rule) -> mod.Rule:
    left = ""
    right = ""
    context = ""
    
    g = r.left
    for v in g.vertices:
        try:
            left += 'node [ id %d label "a(%s, %d, %d)" ]' % (
                v.id, 
                v.atomId.symbol,
                v.charge,
                v.radical
            )
        except mod.libpymod.LogicError as e:
            left += 'node [ id %d label "a(_A, %d, %d)" ]' % (v.id, v.charge, v.radical)
    
    for e in g.edges:
        left += 'edge [ source %d target %d label "e(%s)" ]' % (
            e.source.id, 
            e.target.id, 
            termBondFromBondType[e.bondType]
        )

    g = r.context
    for v in g.vertices:
        if hasattr(v, "atomId"):
            try:
                context += 'node [ id %d label "a(%s, %d, %d)" ]' % (
                    v.id, 
                    v.atomId.symbol,
                    v.charge,
                    v.radical,
                )
            except mod.libpymod.LogicError as e:
                context += 'node [ id %d label "a(_A, %d, %d)" ]' % (v.id, v.charge, v.radical)
    for e in g.edges:
        if hasattr(v, "bondType"):
            context += 'edge [ source %d target %d label "e(%s)" ]' % (
                e.source.id, 
                e.target.id, 
                termBondFromBondType[e.bondType]
            )

    g = r.right
    for v in g.vertices:
        try:
            right += 'node [ id %d label "a(%s, %d, %d)" ]' % (
                v.id, 
                v.atomId.symbol, 
                v.charge, 
                v.radical,
            )
        except mod.libpymod.LogicError as e:
            right += 'node [ id %d label "a(_A, %d, %d)" ]' % (v.id, v.charge, v.radical)
    for e in g.edges:
        right += 'edge [ source %d target %d label "e(%s)" ]' % (
            e.source.id, 
            e.target.id, 
            termBondFromBondType[e.bondType]
        )
        
    s = f"rule [\n\tleft [\n{left}\t]\n\tcontext [\n{context}\t]\n\tright [\n{right}\t]\n]\n"

    return mod.ruleGMLString(s, name=r.name + ", term", add=False)

#===
def ruleFromTerm(r: mod.Rule) -> mod.Rule:
    left = ""
    right = ""
    
    for v in r.left.vertices:
        left += 'node [ id %d label "%s" ]\n' % (v.id, decodeVertexLabel(v.stringLabel))
        #print("v", r.name, decodeVertexLabel(v.stringLabel), v.stringLabel)
    for e in r.left.edges:
        left += 'edge [ source %d target %d label "%s" ]\n' % (e.source.id, e.target.id, decodeEdgeLabel(e.stringLabel))
    
    for v in r.right.vertices:
        right += 'node [ id %d label "%s" ]\n' % (v.id, decodeVertexLabel(v.stringLabel))
    for e in r.right.edges:
        right += 'edge [ source %d target %d label "%s" ]\n' % (e.source.id, e.target.id, decodeEdgeLabel(e.stringLabel))
    
    s = "rule [\n\tleft [\n%s\t]\n\tright [\n%s\t]\n]\n" % (left, right)
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

    return Counter(lines1) == Counter(lines2)