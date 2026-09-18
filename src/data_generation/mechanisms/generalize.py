"""
Generalize a curated mechanism step from the ONE book molecule it was drawn on
into a reusable fragmentation template.

Why this module exists
----------------------
``dfs_writer`` converts a step by writing out the FULL reactant/product graph
exactly as curated, every spectator atom and every spectator hydrogen included.
Because mod matches a rule's left graph by subgraph embedding, such a rule fires
only where a host contains that entire concrete substructure -- in practice,
only on the book molecule itself. Measured over the 172-molecule corpus, the
resulting library produced a mean 4.4 distinct MØD masses per molecule against
30.8 for the hand-authored ``src/data_generation/rules``, i.e. it barely fired
at all (``data/outputs/metrics/ceiling_mechanisms_2026-08-24``).

The corpus already carries the information needed to fix that. Every step
records ``electron_moves`` -- the curator's transcription of the drawn
electron-pushing arrows -- which names the atoms the chemistry actually
involves. Everything else is spectator scaffolding that happened to be in the
book's example compound, and pruning it turns one concrete instance into the
reaction class the book was illustrating.

What is kept
------------
:func:`reacting_core` takes the union of two independent signals:

* the **graph diff** -- every atom whose element/charge/radical/implicit-H
  count changes, plus both endpoints of every bond whose order changes. This is
  ground truth for what the rewrite does; a rule that dropped any of it would
  not be the same reaction.
* the **drawn arrows** -- ``electron_moves``' source/target atom maps.

They agree on 518 of 530 curated steps. The union, not either alone, is used:
the arrows carry the curator's intent where the diff is silent (an atom the
chemist considered part of the mechanism but that happens to come out
unchanged), and the diff catches the 12 steps whose arrows do not account for
the whole change (Kekule shifts around an aromatic ring, ring walks).

:func:`keep_set` then adds, in order:

* **Steiner connectors** -- the atoms on shortest paths between core atoms, on
  BOTH sides' connectivity. Without these a rearrangement's core would fall
  into disconnected pieces and the rule would no longer constrain the ring size
  that makes it that rearrangement (a gamma-H transfer would degenerate into
  "any H reaches any O").
* a **context shell** of ``radius`` bonds around that set. ``radius=0`` is the
  bare reacting core; a large radius converges on the untouched original.
* an **ion anchor** (see below).

The ion anchor
--------------
24% of steps (125/530) carry the precursor's charge on an atom that no arrow
touches and no core path reaches -- a remote charge site. Pruned naively, those
rules lose every mention of a charge and would embed into NEUTRAL substructures,
firing on the neutral halves of earlier fragmentations. That is both wrong for
EI-MS (neutral losses are not further fragmented into the observed ion series)
and a derivation-graph explosion risk. So when the reactant side bears a charge
or an unpaired electron and pruning would discard every atom carrying one, the
nearest such atom is retained along with the path connecting it to the core.
The rule then still asserts "this substructure belongs to an ion", which is the
weakest form of the original constraint rather than none of it.

Spectator hydrogens
-------------------
Handled separately, in ``dfs_writer.plan_implicit_hydrogens``: that function
expands ``min(left_count, right_count)`` unchanged hydrogens per heavy atom into
explicit shared vertices, which pins every matched atom to an exact substitution
(a rule written for a methyl cannot match a methylene). Dropping them is the
single largest generality gain available -- mean atoms written per rule falls
from 22.5 to 9.1 -- and is safe: an unwritten hydrogen is simply not part of the
match, and removing it from both sides symmetrically leaves the conservation
guard's tally unchanged. See that function's ``keep_unchanged`` argument.
"""
from __future__ import annotations

import collections
from typing import Dict, Iterable, List, Set, Tuple

from .dfs_writer import _Graph

# Keep in step with dfs_writer._IMPLICIT_H_ID_BASE: ids at or above it are
# synthetic hydrogen vertices invented during H expansion, which happens after
# pruning and therefore never appears in a keep set.
_SYNTHETIC_ID_BASE = 1_000_000


def _adjacency(graph: _Graph) -> Dict[int, Set[int]]:
    """Undirected neighbour sets, bond order discarded (pruning is topological)."""
    adj: Dict[int, Set[int]] = collections.defaultdict(set)
    for atom_id, neighbours in graph.adjacency.items():
        for other, _token in neighbours:
            adj[atom_id].add(other)
            adj[other].add(atom_id)
    return adj


def _bond_orders(graph: _Graph) -> Dict[frozenset, str]:
    return {
        frozenset((atom_id, other)): token
        for atom_id, neighbours in graph.adjacency.items()
        for other, token in neighbours
    }


def reacting_core(
    left: _Graph, left_h: Dict[int, int],
    right: _Graph, right_h: Dict[int, int],
    arrow_atom_maps: Iterable[int] = (),
) -> Set[int]:
    """The atoms this step's rewrite actually involves: the graph diff between
    the two sides, unioned with the curator's drawn ``electron_moves`` arrows.

    ``arrow_atom_maps`` is every atom-map number appearing as an electron move's
    source or target; ids not present on the reactant side are ignored, so a
    caller may pass the step's whole arrow set without filtering it first.
    """
    core: Set[int] = set()

    for atom_id in set(left.atoms) | set(right.atoms):
        before, after = left.atoms.get(atom_id), right.atoms.get(atom_id)
        if before is None or after is None:
            # An atom present on only one side; check_mapped_atom_sets rejects
            # this for real atoms, but stay defensive rather than silently
            # pruning something the rewrite creates or destroys.
            core.add(atom_id)
            continue
        if (before.symbol, before.charge, before.radical_electrons) != (
            after.symbol, after.charge, after.radical_electrons
        ):
            core.add(atom_id)
        if left_h.get(atom_id, 0) != right_h.get(atom_id, 0):
            core.add(atom_id)

    left_bonds, right_bonds = _bond_orders(left), _bond_orders(right)
    for pair in set(left_bonds) | set(right_bonds):
        if left_bonds.get(pair) != right_bonds.get(pair):
            core |= set(pair)

    return core | (set(arrow_atom_maps) & set(left.atoms))


def _steiner(core: Set[int], adj: Dict[int, Set[int]]) -> Set[int]:
    """``core`` plus the atoms on a shortest path between any two core atoms
    that lie in the same connected component."""
    keep = set(core)
    for source in core:
        parent: Dict[int, int] = {source: None}
        queue = collections.deque([source])
        while queue:
            current = queue.popleft()
            for neighbour in adj[current]:
                if neighbour not in parent:
                    parent[neighbour] = current
                    queue.append(neighbour)
        for target in core:
            if target == source or target not in parent:
                continue
            step = target
            while step is not None:
                keep.add(step)
                step = parent[step]
    return keep


def _grow(seed: Set[int], adj: Dict[int, Set[int]], radius: int) -> Set[int]:
    shell = set(seed)
    for _ in range(radius):
        shell |= {n for atom_id in list(shell) for n in adj[atom_id]}
    return shell


def _path_to_nearest(sources: Set[int], targets: Set[int], adj: Dict[int, Set[int]]) -> Set[int]:
    """Atoms on a shortest path from any atom in ``sources`` to the nearest atom
    in ``targets``; empty if no target is reachable."""
    parent: Dict[int, int] = {s: None for s in sources}
    queue = collections.deque(sources)
    while queue:
        current = queue.popleft()
        if current in targets:
            path = set()
            step = current
            while step is not None:
                path.add(step)
                step = parent[step]
            return path
        for neighbour in adj[current]:
            if neighbour not in parent:
                parent[neighbour] = current
                queue.append(neighbour)
    return set()


def keep_set(
    core: Set[int], left: _Graph, right: _Graph, radius: int,
    anchor_ion: bool = True,
) -> Set[int]:
    """Which reactant atoms the generalized rule writes out.

    ``radius`` is the context shell in bonds around the connected core: 0 keeps
    only the core and the paths between its parts, and a radius at or above the
    molecule's diameter reproduces the untouched original graph.

    With ``anchor_ion``, a reactant that bears a charge or an unpaired electron
    always retains at least one atom carrying one, plus the path joining it to
    the core -- see this module's docstring for why a rule that mentions no
    charge at all is worse than a slightly larger one.
    """
    left_adj, right_adj = _adjacency(left), _adjacency(right)
    keep = _steiner(core, left_adj) | _steiner(core, right_adj)
    keep = _grow(keep, left_adj, radius) | _grow(keep, right_adj, radius)
    keep &= set(left.atoms)

    if anchor_ion and core:
        for carriers in (
            {i for i, a in left.atoms.items() if a.charge != 0},
            {i for i, a in left.atoms.items() if a.radical_electrons != 0},
        ):
            if carriers and not (carriers & keep):
                keep |= _path_to_nearest(set(core), carriers, left_adj) & set(left.atoms)

    return keep


def prune_graph(graph: _Graph, keep: Set[int]) -> None:
    """Drop every atom outside ``keep``, and every bond touching a dropped atom.

    Mutates in place. Applying the same ``keep`` to both sides of a step leaves
    the rule's atom tally balanced, so the conservation guard in
    ``rules/__init__.py`` sees exactly what it saw before pruning.
    """
    for atom_id in [i for i in graph.atoms if i not in keep]:
        del graph.atoms[atom_id]
        del graph.adjacency[atom_id]
    for atom_id, neighbours in graph.adjacency.items():
        graph.adjacency[atom_id] = [(o, t) for o, t in neighbours if o in keep]


__all__ = ["reacting_core", "keep_set", "prune_graph"]
