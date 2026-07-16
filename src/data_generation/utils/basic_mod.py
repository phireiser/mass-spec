"""
Basic MØD utilities
graph traversal, filtering
"""

from typing import List, Set, Optional
import mod


def graph_from_smiles(smiles: str, name: Optional[str] = None) -> mod.Graph:
    """
    Build a molecule graph from SMILES, keeping aromatic rings aromatic.

    Aromatic bonds now ride through the fragmentation pipeline as the inert term
    ``e(ar)`` (see :func:`data_generation.utils.term_transfers.term_from_graph`),
    so the molecule is NOT kekulised. This is deliberate: kekulising commits the
    ring to one arbitrary Kekulé form, and because the term-mode rules match on
    exact bond order, that arbitrary choice would change which fragments are
    reachable (resonance-dependent fragmentation). Left aromatic, the ring carries
    no alternation to be arbitrary about, and only the curated aromatic rules can
    match it -- generic integer-bond-order rules cannot touch an ``e(ar)`` ring.

    ``mod.Graph.fromSMILES`` perceives aromaticity but *preserves* explicit bonds,
    so a SMILES written in some arbitrary Kekulé form would flow through Kekulé and
    stay resonance-dependent. To make the fix robust to input form, we first
    canonicalise through RDKit (whose default SMILES writes aromatic rings in the
    lowercase aromatic form); mod then perceives ``mod.BondType.Aromatic`` ring
    bonds -> term ``e(ar)``. If RDKit cannot parse the input, the raw SMILES is used.
    """
    try:
        from rdkit import Chem
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            smiles = Chem.MolToSmiles(mol)  # default: aromatic (kekuleSmiles=False)
    except Exception:
        pass
    return mod.Graph.fromSMILES(smiles, name) if name is not None \
        else mod.Graph.fromSMILES(smiles)


def get_parents(
    dg: mod.DG,
    frag: mod.Graph
    ) -> List[mod.Graph]:
    """
    Get parents of a fragment in the derivation graph.
    """
    dg_vert = dg.findVertex(frag)
    parents = []
    for in_edge in dg_vert.inEdges:
        parents.extend(x.graph for x in in_edge.sources)
    return parents


def filter_ancestors_out(
    fragments: List[mod.Graph],
    dg: mod.DG,
    max_depth: Optional[int] = None,
) -> List[mod.Graph]:
    """
    Keep only those fragments that are NOT an ancestor of any other fragment.

    - fragments: graphs (molecules) in the derivation graph
    - dg: the derivation graph
    - max_depth: optional cap on parent-traversal depth (None = unlimited)

    Returns a list of fragments that are 'terminal' w.r.t. the partial order
    (i.e., not an ancestor of another input fragment).
    """

    # Collect all ancestors of any fragment in the input
    all_ancestors: Set[mod.Graph] = set()

    for f in fragments:
        # Upward traversal with cycle protection
        stack = get_parents(dg, f)
        visited: Set[mod.Graph] = set()
        depth = 0

        while stack:
            # Depth control
            if max_depth is not None and depth >= max_depth:
                break

            next_level = []
            for p in stack:
                if p in visited:
                    continue
                visited.add(p)

                all_ancestors.add(p)
                next_level.extend(get_parents(dg, p))
            stack = next_level
            depth += 1

    # Keep fragments that are NOT ancestors of any other fragment
    return [f for f in fragments if f not in all_ancestors]

def get_out_edges_by_vertex_id(dg: mod.DG, v_id: int) -> List[int]:
    """
    Return the IDs of outgoing hyperedges for a vertex identified by its mod ID.
    """
    return [e.id for e in next(v.outEdges for v in dg.vertices if v.id == v_id)]

def get_rule_ids_by_edge_id(dg: mod.DG, eid: int) -> List[int]:
    """
    Return the mod IDs of the rules of a specific edge identified by its mod ID.
    """
    edge = next(e for e in dg.edges if e.id == eid)
    return [r.id for r in edge.rules]

def get_fragment_ids_by_edge_id(dg: mod.DG, eid: int) -> List[int]:
    """
    Return the mod IDs of the target graphs of a specific edge identified by its mod ID.
    """
    edge = next(e for e in dg.edges if e.id == eid)
    return [t.id for t in edge.targets]


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "graph_from_smiles",
    "get_parents",
    "filter_ancestors_out",
    "get_out_edges_by_vertex_id",
    "get_rule_ids_by_edge_id",
    "get_fragment_ids_by_edge_id",
]
