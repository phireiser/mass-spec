"""
Basic MØD utilities
graph traversal, filtering
"""

from typing import List, Set, Optional
import mod

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
    "get_parents",
    "filter_ancestors_out",
    "get_out_edges_by_vertex_id",
    "get_rule_ids_by_edge_id",
    "get_fragment_ids_by_edge_id",
]
