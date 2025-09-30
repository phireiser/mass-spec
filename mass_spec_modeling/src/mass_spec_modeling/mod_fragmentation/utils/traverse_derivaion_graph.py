"""all hypergraph traversel functions"""

from typing import List, Set, Optional
import mod

def get_parents(
    dg: mod.DG,
    frag: mod.Graph
    ) -> List[mod.Graph]:
    """get parents of a fragment in the derivation graph"""
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

    - fragments: gaphs molecules in the derivation graph
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
