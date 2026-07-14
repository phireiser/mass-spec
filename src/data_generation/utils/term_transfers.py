"""
for and back transformations from term mode to string mode
"""

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
        symbol, charge, radical = encode_vertex_label(v.stringLabel)
        s += f'node [ id {v.id} label "a({symbol}, {charge}, {radical})" ]'

    for e in g.edges:
        bond_type = term_bond_from_bond_type[e.bondType]
        if bond_type.startswith("__error"):
            raise ValueError(
                f"term_from_graph: {g.name!r} has a {e.bondType} bond, which has "
                f"no term-mode encoding. Aromatic bonds must be kekulised to "
                f"explicit single/double bonds first -- build the molecule with "
                f"utils.graph_from_smiles (or pass a Kekulé SMILES)."
            )
        s += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'
    s +="]\n"
    return mod.Graph.fromGMLString(s, name=g.name + ", term", add=False)


def decode_vertex_label(l: str) -> str:
    """
    takes a vertex in term-bracketed expression and
    returns a compact stringLabel representation of atom
    """

    assert l.startswith("a(")
    assert l.endswith(")")
    l = l[2:-1].split(", ")
    lab = l[0]
    c = int(l[1])
    r = int(l[2])
    if c > 0:
        lab += "+" * c
    elif c < 0:
        lab += "-" * abs(c)
    if r > 0: # not elif otherwise vertex can't be charged radical
        lab += "." * r
    return lab


def encode_vertex_label(string_label: str) -> "tuple[str, int, int]":
    """
    Inverse of :func:`decode_vertex_label`: parse a compact string-mode atom
    label such as ``'C..'``, ``'C+.'`` or ``'O-'`` into ``(symbol, charge,
    radical)``.

    Radicals are counted from the number of ``'.'`` characters, so biradicals
    /carbenes (``'..'``) survive. This is the crucial difference from reading
    ``int(v.radical)`` (mod's ``radical`` is a *boolean*, capping at 1) or
    ``v.atomId.symbol`` (raises ``LogicError`` for non-concrete atoms like
    ``'C..'``, which previously collapsed the symbol to the ``_A`` placeholder).

    A non-element leading token (wildcard ``'*'``, the ``_A`` placeholder, etc.)
    maps back to ``_A`` to preserve the previous placeholder semantics.
    """
    i = 0
    while i < len(string_label) and string_label[i] not in "+-.":
        i += 1
    symbol = string_label[:i]
    deco = string_label[i:]
    charge = deco.count("+") - deco.count("-")
    radical = deco.count(".")
    if not symbol.isalpha():  # wildcard / placeholder / query atom
        symbol = "_A"
    return symbol, charge, radical


def decode_edge_label(l: str) -> str:
    """
    takes a edge in term-bracketed expression and
    returns a compact string representation of atom
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


# The term->string conversion is a pure function of the input graph's atoms and
# bonds, but the `sub_group` predicate calls it on the same handful of fragment
# graphs hundreds of thousands of times (once per BFS/DFS rebuild per derivation),
# and each call pays a full GML round-trip through `mod.Graph.fromGMLString`
# (~1.2M calls / ~210s cumulative on toluene). We memoise on `mod.Graph.id`, a
# stable, process-unique, never-reused integer -- crucially NOT `id(g)`, because
# mod hands out a *fresh* Python wrapper on every access so `id(g)` never repeats.
# The distinct-graph count equals the DG size (tens), so the cache stays tiny while
# collapsing the millions of calls to a few real conversions.
_graph_from_term_cache: "dict[int, mod.Graph]" = {}


def clear_graph_from_term_cache() -> None:
    """Drop the memoised term->string conversions (call between mod universes/tests)."""
    _graph_from_term_cache.clear()


def graph_from_term(g: mod.Graph) -> mod.Graph:
    """
    takes a graph in of string mode and returns a graph for term mode
    """

    gid = getattr(g, "id", None)
    if gid is not None:
        cached = _graph_from_term_cache.get(gid)
        if cached is not None:
            return cached

    s = "graph [\n"
    for v in g.vertices:
        label = decode_vertex_label(v.stringLabel)
        s += f'node [ id {v.id} label "{label}" ]\n'
    for e in g.edges:
        edge_label = decode_edge_label(e.stringLabel)
        # I don't kown why I need to exchange target and source
        s += f'edge [ source {e.target.id} target {e.source.id} label "{edge_label}" ]\n'
    s += "]\n"
    result = mod.Graph.fromGMLString(s, name= getattr(g, "name", "").replace(", term", ""), add=False)
    if gid is not None:
        _graph_from_term_cache[gid] = result
    return result


def parse_term_atom(string_label: str) -> "tuple[str, int, int]":
    """
    Parse a term vertex label ``a(symbol, charge, radical)`` into its parts.

    Returns ``(symbol, charge, radical)``. This is the cheap, parse-only
    counterpart to round-tripping a term graph back into string mode via
    :func:`graph_from_term` when only the atom's scalar properties are needed.
    """
    assert string_label.startswith("a(") and string_label.endswith(")"), \
        f"not a term atom label: {string_label!r}"
    symbol, charge, radical = (part.strip() for part in string_label[2:-1].split(","))
    return symbol, int(charge), int(radical)


# Per-element exact (monoisotopic) masses, sourced from mod itself so the values
# match mod's own ``Graph.exactMass`` exactly. Summing these over a graph's atoms
# reproduces ``graph_from_term(g).exactMass`` without the GML round-trip (verified
# bit-for-bit on representative molecules). Lazily populated and cached.
_atom_exact_mass_cache: "dict[str, float]" = {}


def atom_exact_mass(symbol: str) -> float:
    """Exact monoisotopic mass of a single (neutral) ``symbol`` atom, as mod reports it."""
    mass = _atom_exact_mass_cache.get(symbol)
    if mass is None:
        g = mod.Graph.fromGMLString(
            f'graph [ node [ id 0 label "{symbol}" ] ]', add=False
        )
        mass = g.exactMass
        _atom_exact_mass_cache[symbol] = mass
    return mass


# Atomic number per element symbol, read from mod's own atom data. 0 for
# placeholders/non-elements (wildcards, the ``_A`` placeholder). Lazily cached.
_atomic_number_cache: "dict[str, int]" = {}


def atomic_number(symbol: str) -> int:
    """Atomic number of an element ``symbol``; ``0`` for placeholders/non-elements."""
    n = _atomic_number_cache.get(symbol)
    if n is None:
        try:
            g = mod.Graph.fromGMLString(
                f'graph [ node [ id 0 label "{symbol}" ] ]', add=False
            )
            n = int(next(iter(g.vertices)).atomId)
        except (mod.libpymod.LogicError, ValueError, StopIteration):
            n = 0
        _atomic_number_cache[symbol] = n
    return n


# Electron mass, taken from mod (H minus H+) so it matches mod's own bookkeeping
# exactly. mod's ``exactMass`` charges the ion: a cation has lost electrons and
# weighs less, an anion has gained them. Summing neutral atomic masses therefore
# overshoots by ``net_charge`` electron masses, which we subtract back off.
_electron_mass_cache: "list[float]" = []


def electron_mass() -> float:
    """Electron rest mass in u, as implied by mod's exact masses (H - H+)."""
    if not _electron_mass_cache:
        h = mod.Graph.fromGMLString('graph [ node [ id 0 label "H" ] ]', add=False)
        hp = mod.Graph.fromGMLString('graph [ node [ id 0 label "H+" ] ]', add=False)
        _electron_mass_cache.append(h.exactMass - hp.exactMass)
    return _electron_mass_cache[0]


def net_charge_from_term(g: mod.Graph) -> int:
    """
    Net formal charge of a term-mode graph, summed straight from the vertex
    labels. Equivalent to ``smiles.count('+') - smiles.count('-')`` on the
    round-tripped string-mode molecule, but without building a canonical SMILES
    or reconstructing the molecule.
    """
    return sum(parse_term_atom(v.stringLabel)[1] for v in g.vertices)


def exact_mass_from_term(g: mod.Graph) -> "float | None":
    """
    Exact (monoisotopic) mass of a term-mode graph, summed from per-atom masses
    and corrected for the ion's electron count, matching mod's ``exactMass``.

    Returns ``None`` if any vertex carries a non-element (placeholder) symbol,
    mirroring the ``isMolecule`` guard callers previously used on the
    round-tripped string-mode graph: a graph with placeholder atoms is not a
    concrete molecule and has no well-defined mass.
    """
    total = 0.0
    net_charge = 0
    for v in g.vertices:
        symbol, charge, _ = parse_term_atom(v.stringLabel)
        try:
            total += atom_exact_mass(symbol)
        except mod.libpymod.LogicError:
            # non-element / placeholder symbol -> not a concrete molecule
            return None
        net_charge += charge
    return total - net_charge * electron_mass()


def term_from_rule(r: mod.Rule) -> mod.Rule:
    """
    takes a rule for term mode and returns a rule for string mode
    """

    left = ""
    right = ""
    context = ""

    g = r.left
    for v in g.vertices:
        symbol, charge, radical = encode_vertex_label(v.stringLabel)
        left += f'node [ id {v.id} label "a({symbol}, {charge}, {radical})" ]'

    for e in g.edges:
        bond_type = term_bond_from_bond_type[e.bondType]
        left += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'
    g = r.context
    for v in g.vertices:
        if hasattr(v, "atomId"):
            symbol, charge, radical = encode_vertex_label(v.stringLabel)
            context += f'node [ id {v.id} label "a({symbol}, {charge}, {radical})" ]'
    for e in g.edges:
        if hasattr(v, "bondType"):
            bond_type = term_bond_from_bond_type[e.bondType]
            context += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'
    g = r.right
    for v in g.vertices:
        symbol, charge, radical = encode_vertex_label(v.stringLabel)
        right += f'node [ id {v.id} label "a({symbol}, {charge}, {radical})" ]'
    for e in g.edges:
        bond_type = term_bond_from_bond_type[e.bondType]
        right += f'edge [ source {e.source.id} target {e.target.id} label "e({bond_type})" ]'

    s = f"rule [\n\tleft [\n{left}\t]\n\tcontext [\n{context}\t]\n\tright [\n{right}\t]\n]\n"

    return mod.Rule.fromGMLString(s, name=r.name + ", term", add=False)


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
    return mod.Rule.fromGMLString(s, name = r.name.replace(", term", ""), add=False)


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "term_from_graph",
    "term_from_rule",
    "graph_from_term",
    "clear_graph_from_term_cache",
    "rule_from_term",
    "parse_term_atom",
    "atom_exact_mass",
    "electron_mass",
    "net_charge_from_term",
    "exact_mass_from_term",
]
