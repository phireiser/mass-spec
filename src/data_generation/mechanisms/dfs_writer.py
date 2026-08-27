"""
Convert one curated mechanism-record elementary step into mod's ``Rule.fromDFS``
string grammar.

The grammar below was reverse-engineered from the ~190 hand-authored rules in
``src/data_generation/rules`` (there is no local ``mod`` install to test
against outside the project container -- see that package's own DFS strings
for the ground truth this was checked against):

* Every atom is written ``[SYMBOL<charge><radical>]<id>``, where ``<charge>``
  is ``+`` or ``-`` repeated once per unit of formal charge, ``<radical>`` is
  ``.`` repeated once per unpaired electron, and ``<id>`` is a permanent
  integer vertex id (arbitrary size, e.g. ``[H]12``) -- unlike SMILES ring
  digits, this id is never reused/freed and doubles as the atom-map number
  linking an atom to itself across the ``>>``.
* A bond between two atoms just-declared in sequence (a tree edge) is written
  with an explicit order token immediately before the second atom: ``{=}``
  double, ``{#}`` triple, ``:`` aromatic; a plain single bond has NO token.
  A ring-closure/back-edge (bond to an already-declared id) is written the
  same way but bare (no brackets, no symbol) -- ``{-}3`` -- and here the
  token is NEVER omitted, even for a single bond (confirmed by
  ``wikipedia.py``'s ``dielsAdler_1``: ``...[C]6{-}1``).
* Branches use SMILES-style parentheses. At an atom with more than one
  remaining (unvisited-or-back-edge) neighbour, all but one are individually
  wrapped in ``(...)``; the remaining one continues the string unwrapped.
  Which one is left unwrapped: if any remaining neighbour is a not-yet-
  written HEAVY (non-H) atom, the one with the largest id continues unwrapped
  and everything else (other heavy atoms, all hydrogens, all back-edges) is
  wrapped. If none is heavy (e.g. three trailing implicit hydrogens), every
  remaining neighbour is wrapped and nothing continues unwrapped. If exactly
  one neighbour remains of ANY kind (including a lone back-edge), it is
  always written unwrapped. This is the minimal rule consistent with every
  branching/ring/all-H-leaf example in the existing rule files.
* Disconnected components (e.g. an ion plus its neutral loss) are joined with
  a bare ``.`` at the top level, outside any brackets -- distinguishable from
  a radical-dot only by nesting depth, exactly as in SMILES.

SCOPE: this reads the mapped SMILES exactly as RDKit parses them (including
RDKit's own per-atom formal-charge/radical perception -- confirmed against
curated records' own curator notes, e.g. "[O+:7] with two bonds = one
unpaired electron in RDKit"), NOT the species-level aggregate
``charge``/``radical_electrons`` fields, which the schema itself documents as
authoritative for the overall electronic STATE but which carry no per-atom
localisation -- some precursors (e.g. a plain, undecorated SMILES for a
sigma-ionized M+*, matching this project's own delocalized-charge model)
legitimately carry no per-atom localisation at all. This module does not
itself decide that a mismatch is fatal; :func:`mapped_smiles_charge_and_radical`
exposes the per-atom sum so ``build_rules.py`` can cross-check it against the
species-level totals and decide whether to reconstruct a localisation (see
:func:`apply_localization`) or skip with a clear reason.

TWO RECONSTRUCTIONS this module can perform, both driven by information the
record already contains rather than any outside guess -- see each function's
own docstring for exactly when it applies and why it's safe:

* :func:`apply_localization` -- transplant a product's charge/radical
  PLACEMENT back onto the same atom (by atom-map id) in an otherwise
  unlocalized precursor.
* :func:`plan_implicit_hydrogens` -- reconcile a hydrogen that visibly moves
  between two heavy atoms' aggregate H-counts (e.g. "CH3" on one side,
  "CH2" on the other) but was never given its own atom-map number, by
  pairing up the losing and gaining atoms and synthesizing the missing
  shared identity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from rdkit import Chem

# mod's bond-order tokens, keyed by RDKit's BondType. A tree edge omits the
# token entirely for SINGLE (see module docstring); callers handle that case.
_BOND_TOKENS = {
    Chem.BondType.SINGLE: "-",
    Chem.BondType.DOUBLE: "=",
    Chem.BondType.TRIPLE: "#",
    Chem.BondType.AROMATIC: ":",
}

# Vertex ids for synthesized (implicit or inferred-moving) hydrogens start
# here and count up (see plan_implicit_hydrogens), comfortably above any
# curator-assigned atom-map number in this corpus (small, page-scale
# integers -- see RESUME.md's numbering schemes, none past the low tens).
_IMPLICIT_H_ID_BASE = 1_000_000


class MechanismConversionError(ValueError):
    """A mechanism step could not be converted to a mod DFS rule string."""


@dataclass
class _Atom:
    id: int
    symbol: str
    charge: int
    radical_electrons: int

    def label(self) -> str:
        deco = ("+" * self.charge) if self.charge > 0 else ("-" * -self.charge)
        deco += "." * self.radical_electrons
        return f"[{self.symbol}{deco}]"


@dataclass
class _Graph:
    atoms: Dict[int, _Atom] = field(default_factory=dict)
    adjacency: Dict[int, List[Tuple[int, str]]] = field(default_factory=dict)

    def add_atom(self, atom: _Atom) -> None:
        if atom.id in self.atoms:
            raise MechanismConversionError(
                f"duplicate atom-map id {atom.id} within one reaction side"
            )
        self.atoms[atom.id] = atom
        self.adjacency[atom.id] = []

    def add_bond(self, a: int, b: int, token: str) -> None:
        self.adjacency[a].append((b, token))
        self.adjacency[b].append((a, token))


def mapped_smiles_charge_and_radical(smiles: str) -> Tuple[int, int]:
    """Sum of per-atom formal charge and radical-electron count over ``smiles``.

    For cross-checking against a curated state's SPECIES-LEVEL aggregate
    ``charge``/``radical_electrons`` fields (see :mod:`build_rules`): some
    precursor species in this corpus -- by design, not error -- record their
    charge/radical only at the species level (e.g. a plain, undecorated
    ``propane_radical_cation`` SMILES for a sigma-ionized M+*, matching this
    project's own delocalized-charge model in ``core/strategy.py``, where the
    charge/radical genuinely has no single-atom localisation prior to
    fragmentation). A mod rule's LEFT graph must match a concretely-localized
    species, so such a step cannot become a useful rule and should be skipped
    with a clear reason rather than mis-converted.
    """
    params = Chem.SmilesParserParams()
    params.removeHs = False
    mol = Chem.MolFromSmiles(smiles, params)
    if mol is None:
        raise MechanismConversionError(f"RDKit could not parse mapped SMILES: {smiles!r}")
    return (
        sum(atom.GetFormalCharge() for atom in mol.GetAtoms()),
        sum(atom.GetNumRadicalElectrons() for atom in mol.GetAtoms()),
    )


def apply_localization(graph: "_Graph", source: "_Graph") -> None:
    """Mutate ``graph`` in place: every atom id present in BOTH ``graph`` and
    ``source`` takes ``source``'s charge/radical_electrons.

    Used to transplant a product state's charge/radical PLACEMENT back onto a
    precursor recorded without any per-atom localisation (a plain, undecorated
    SMILES for a delocalized M+*, see :func:`mapped_smiles_charge_and_radical`).
    Atom identity persists across a single elementary step by construction, so
    "the atom that ends up charged/radical in THIS product" is exactly the
    physically sensible localisation for the precursor state that leads to
    THIS specific pathway -- not a guess, just reading the destination back
    onto the same, already-identified atom. Callers (``build_rules.py``)
    decide WHEN this is appropriate (only for a state that is completely
    unlocalized to begin with) and verify the result actually sums to the
    state's declared totals; this function only does the mechanical part.
    """
    for atom_id, atom in graph.atoms.items():
        source_atom = source.atoms.get(atom_id)
        if source_atom is not None:
            atom.charge = source_atom.charge
            atom.radical_electrons = source_atom.radical_electrons


def check_mapped_atom_sets(left: "_Graph", right: "_Graph") -> None:
    """Raise if the reactant/product side disagree on which REAL (curator-
    mapped) atom ids are present -- i.e. an atom would have to be created or
    destroyed outright rather than rearranged. Synthetic implicit-hydrogen ids
    are excluded; those are reconciled separately by
    :func:`plan_implicit_hydrogens`."""
    left_mapped = {i for i in left.atoms if i < _IMPLICIT_H_ID_BASE}
    right_mapped = {i for i in right.atoms if i < _IMPLICIT_H_ID_BASE}
    if left_mapped != right_mapped:
        raise MechanismConversionError(
            "mapped atom set differs between reactant and product state (an "
            "atom would have to be created/destroyed rather than rearranged): "
            f"only in reactants={sorted(left_mapped - right_mapped)}, "
            f"only in products={sorted(right_mapped - left_mapped)}"
        )


def plan_implicit_hydrogens(
    left_h: Dict[int, int], right_h: Dict[int, int],
) -> Tuple[Dict[int, List[int]], Dict[int, List[int]], int]:
    """Decide which synthetic hydrogen-vertex ids attach to which heavy atom
    on each side, reconciling any atom whose implicit-H count changes.

    For each heavy atom, ``min(left_count, right_count)`` hydrogens are
    ordinary SHARED spectators -- unmoved, same id on both sides, exactly as
    before. Any EXCESS on the left (an atom that loses hydrogens) and any
    excess on the right (an atom that gains them) are pooled separately and
    paired up 1:1 -- each pair gets one new id shared between the losing
    atom (on the left) and the gaining atom (on the right), modeling an
    UNMAPPED hydrogen migration the curator's aggregate H-count notation
    (e.g. writing "CH3" on one side and "CH2" on the other) implies but did
    not individually atom-map. This is safe because bare hydrogens attached
    to the same heavy atom are chemically interchangeable -- WHICH of an
    atom's hydrogens is "the one that moves" is not a meaningful question,
    only WHETHER the counts can be reconciled at all is.

    Raises if the total deficit and total surplus across the whole state
    don't match -- that is not a simple relocation (e.g. an external
    reagent/proton not captured as a mapped species), and inventing a
    reconciliation would silently paper over that.

    Returns ``(left_plan, right_plan, n_inferred_moves)``, each plan mapping
    ``heavy_atom_id -> [hydrogen_vertex_id, ...]`` for :func:`expand_implicit_hydrogens`.
    """
    left_plan: Dict[int, List[int]] = {}
    right_plan: Dict[int, List[int]] = {}
    deficits: List[int] = []   # heavy atom ids, one entry per "missing" H
    surpluses: List[int] = []  # heavy atom ids, one entry per "new" H
    next_id = _IMPLICIT_H_ID_BASE

    for atom_id in sorted(set(left_h) | set(right_h)):
        left_count = left_h.get(atom_id, 0)
        right_count = right_h.get(atom_id, 0)
        shared = min(left_count, right_count)
        if shared:
            ids = list(range(next_id, next_id + shared))
            next_id += shared
            left_plan[atom_id] = list(ids)
            right_plan[atom_id] = list(ids)
        deficits.extend([atom_id] * (left_count - shared))
        surpluses.extend([atom_id] * (right_count - shared))

    if len(deficits) != len(surpluses):
        raise MechanismConversionError(
            "implicit hydrogen count changes do not balance across the whole "
            f"state (reactant atoms lose {len(deficits)} hydrogen(s) total, "
            f"product atoms gain {len(surpluses)} total) -- not a simple "
            "relocation (e.g. an external reagent/proton not captured as a "
            "mapped species), so it cannot be inferred"
        )

    for from_atom, to_atom in zip(deficits, surpluses):
        h_id = next_id
        next_id += 1
        left_plan.setdefault(from_atom, []).append(h_id)
        right_plan.setdefault(to_atom, []).append(h_id)

    return left_plan, right_plan, len(deficits)


def expand_implicit_hydrogens(graph: "_Graph", plan: Dict[int, List[int]]) -> None:
    """Add one explicit H atom+bond per id in ``plan[heavy_atom_id]``, mutating
    ``graph`` in place. ``plan`` comes from :func:`plan_implicit_hydrogens`."""
    for atom_id, h_ids in plan.items():
        for h_id in h_ids:
            graph.add_atom(_Atom(id=h_id, symbol="H", charge=0, radical_electrons=0))
            graph.add_bond(atom_id, h_id, "-")


def dfs_string_for_state(graph: "_Graph") -> str:
    """Public entry point for emitting one already-fully-built (mapped atoms
    + expanded implicit hydrogens + any localisation patch already applied)
    reaction side as a DFS string."""
    return _dfs_string_for_graph(graph)


def parse_mapped_smiles(smiles: str) -> Tuple[_Graph, Dict[int, int]]:
    """Parse one (possibly multi-component) mapped-SMILES reaction side into
    its CORE graph: every curator-mapped atom (heavy or individually-mapped
    hydrogen) and the bonds between them, WITHOUT expanding implicit
    hydrogens yet (see :func:`plan_implicit_hydrogens` /
    :func:`expand_implicit_hydrogens` for that, done once both sides of a
    reaction are known so a hydrogen moving between them can be reconciled).

    Returns ``(graph, implicit_h_counts)``, where ``implicit_h_counts`` maps
    ``heavy_atom_id -> count`` from RDKit's own per-atom accounting.
    """
    # ``removeHs=False`` is required, not cosmetic: RDKit's default parser folds
    # ANY trivial explicit hydrogen -- including one carrying its own atom-map
    # number, e.g. a curated migrating H -- back into its parent's implicit H
    # count and silently drops the atom (verified empirically; the map number is
    # not by itself a reason RDKit's default RemoveHs keeps it). That would
    # silently corrupt exactly the individually-mapped-hydrogen case this corpus
    # relies on for rearrangement steps, so hydrogens are kept explicit here and
    # only intentionally implicit ones are expanded below.
    parser_params = Chem.SmilesParserParams()
    parser_params.removeHs = False
    mol = Chem.MolFromSmiles(smiles, parser_params)
    if mol is None:
        raise MechanismConversionError(f"RDKit could not parse mapped SMILES: {smiles!r}")

    id_of: Dict[int, int] = {}
    for atom in mol.GetAtoms():
        map_num = atom.GetAtomMapNum()
        if map_num <= 0:
            raise MechanismConversionError(
                f"atom (idx {atom.GetIdx()}, {atom.GetSymbol()}) in {smiles!r} has "
                "no atom-map number; every atom (including any hydrogen written "
                "explicitly, e.g. a migrating H) must be mapped -- unmapped "
                "hydrogens must instead stay implicit"
            )
        id_of[atom.GetIdx()] = map_num

    graph = _Graph()
    for atom in mol.GetAtoms():
        vid = id_of[atom.GetIdx()]
        graph.add_atom(_Atom(
            id=vid,
            symbol=atom.GetSymbol(),
            charge=atom.GetFormalCharge(),
            radical_electrons=atom.GetNumRadicalElectrons(),
        ))

    for bond in mol.GetBonds():
        a = id_of[bond.GetBeginAtomIdx()]
        b = id_of[bond.GetEndAtomIdx()]
        token = _BOND_TOKENS.get(bond.GetBondType())
        if token is None:
            raise MechanismConversionError(
                f"unsupported bond type {bond.GetBondType()!s} in {smiles!r}"
            )
        graph.add_bond(a, b, token)

    implicit_h_counts: Dict[int, int] = {
        id_of[atom.GetIdx()]: atom.GetTotalNumHs()
        for atom in mol.GetAtoms()
        if atom.GetSymbol() != "H"
    }

    return graph, implicit_h_counts


def _dfs_string_for_component(graph: _Graph, root: int) -> str:
    visited: set = {root}

    # Edges are undirected but ``graph.adjacency`` lists each one from both
    # endpoints; ``consumed`` records edges (as a frozenset of their two atom
    # ids) already written, whichever endpoint's turn happened to write it,
    # so a ring bond is emitted exactly once regardless of which of its two
    # endpoints is visited (and therefore looks at that edge) first.
    consumed: set = set()

    def emit(node: int, other: int, token: str) -> str:
        """Write the bond+atom (or bond+back-reference) for one edge, exactly
        once. Re-checks ``visited`` at the moment of writing rather than at
        classification time: two ring bonds sharing ``node`` as their hub
        (e.g. a 3-membered ring through ``node``) can have their far endpoint
        visited by the FIRST bond's recursion before the SECOND bond -- to
        the same physical neighbour -- is written, which must then degrade
        from a tree recursion to a bare ring-closure reference rather than
        re-entering an already-written subtree."""
        consumed.add(frozenset((node, other)))
        if other not in visited:
            visited.add(other)
            body = recurse(other)
            is_tree = True
        else:
            body = str(other)
            is_tree = False
        # Tree edges omit the token for a plain single bond; ring closures
        # (back-edges) never omit it, even for single ("-" -> "{-}").
        if is_tree and token == "-":
            bond_token = ""
        elif token == ":":
            bond_token = ":"
        else:
            bond_token = f"{{{token}}}"
        return f"{bond_token}{body}"

    def recurse(node: int) -> str:
        text = f"{graph.atoms[node].label()}{node}"

        # The edge back to whichever atom called us here (if any) is already
        # in ``consumed`` -- ``emit`` marks an edge consumed BEFORE recursing
        # into its far endpoint -- so it is naturally skipped by the
        # ``edge in consumed`` check below with no separate parent-tracking.
        remaining: List[Tuple[int, str, bool]] = []  # (other, token, is_tree_child)
        for other, token in sorted(graph.adjacency[node]):
            edge = frozenset((node, other))
            if edge in consumed:
                continue
            # Classification snapshot for choosing the unwrapped continuation
            # below; ``emit`` re-checks ``visited`` itself before writing, so
            # a stale "tree" guess here (invalidated by a sibling branch
            # written first) is harmless -- it only affects which candidate
            # is preferred as the continuation, not correctness.
            remaining.append((other, token, other not in visited))

        if not remaining:
            return text

        if len(remaining) == 1:
            continuation = remaining[0]
            wrapped = []
        else:
            heavy_children = [
                r for r in remaining if r[2] and graph.atoms[r[0]].symbol != "H"
            ]
            if heavy_children:
                continuation = max(heavy_children, key=lambda r: r[0])
                wrapped = [r for r in remaining if r[0] != continuation[0]]
            else:
                continuation = None
                wrapped = remaining

        for other, token, _ in wrapped:
            if frozenset((node, other)) in consumed:
                continue  # claimed by an earlier sibling's subtree in the meantime
            text += f"({emit(node, other, token)})"
        if continuation is not None:
            other, token, _ = continuation
            if frozenset((node, other)) not in consumed:
                text += emit(node, other, token)

        return text

    return recurse(root)


def _dfs_string_for_graph(graph: _Graph) -> str:
    if not graph.atoms:
        raise MechanismConversionError("empty reaction side (no atoms)")

    visited: set = set()
    components: List[List[int]] = []
    for start in sorted(graph.atoms):
        if start in visited:
            continue
        stack = [start]
        visited.add(start)
        comp = []
        while stack:
            node = stack.pop()
            comp.append(node)
            for other, _ in graph.adjacency[node]:
                if other not in visited:
                    visited.add(other)
                    stack.append(other)
        components.append(comp)

    components.sort(key=min)
    return ".".join(_dfs_string_for_component(graph, min(comp)) for comp in components)


def compile_parsed_state(
    left: _Graph, left_h: Dict[int, int], right: _Graph, right_h: Dict[int, int],
) -> Tuple[str, int]:
    """Shared final assembly, once both sides are parsed (and, if needed,
    charge/radical-patched via :func:`apply_localization`): validate atom
    identity, reconcile implicit hydrogens, expand them into both graphs, and
    emit the DFS string. Returns ``(dfs_string, n_inferred_h_moves)``.
    """
    check_mapped_atom_sets(left, right)
    left_plan, right_plan, n_moves = plan_implicit_hydrogens(left_h, right_h)
    expand_implicit_hydrogens(left, left_plan)
    expand_implicit_hydrogens(right, right_plan)
    return f"{dfs_string_for_state(left)}>>{dfs_string_for_state(right)}", n_moves


def reaction_dfs_string(left_smiles: str, right_smiles: str) -> str:
    """Compile one elementary step's ``reactants>>products`` mapped SMILES
    directly, with no charge/radical patching. ``left_smiles``/``right_smiles``
    are each the ``.``-joined ``mapped_smiles`` of every species in the step's
    ``from_state``/``to_state``. Raises :class:`MechanismConversionError` if
    the step cannot be expressed as a mod DFS rule (unmapped atom, an atom
    created/destroyed outright rather than rearranged, or an implicit
    hydrogen count change that cannot be reconciled -- see
    :func:`plan_implicit_hydrogens`).

    Callers that may need :func:`apply_localization` first (an unlocalized
    precursor -- see ``build_rules.py``) should call :func:`parse_mapped_smiles`
    and :func:`compile_parsed_state` directly instead, patching the parsed
    left graph in between.
    """
    left, left_h = parse_mapped_smiles(left_smiles)
    right, right_h = parse_mapped_smiles(right_smiles)
    dfs, _n_moves = compile_parsed_state(left, left_h, right, right_h)
    return dfs
