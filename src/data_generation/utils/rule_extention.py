"""
rule extension helper functions
Refactored to delegate diagnostics, mapping, traversal, and label utils.
"""
import re
from functools import lru_cache
from typing import List, Tuple
import mod

from .traversal import vertex_by_id


@lru_cache(maxsize=None)
def _parse_generalization_positions(
    generalization_extention: str
    ) -> Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[Tuple[int, int], ...]]:
    """Parse a rule's §-extension string into 0-based structure indices.

    Pure function of the extension string, which is constant per rule. The
    ``sub_group`` predicate calls :func:`transfer_positions_of_generalization_extention`
    once per rule->molecule match (~10^3 per derivation) and the regex parse is
    identical across every one of them -- only the match-dependent vertex mapping
    varies -- so we memoise the parse. There are only ~65 distinct extension
    strings (one per §-rule), so the cache stays tiny.
    """
    alkyl = tuple(int(x) - 1 for x in re.findall(r'R(\d+)', generalization_extention))
    hetro = tuple(int(x) - 1 for x in re.findall(r'Y(\d+)', generalization_extention))
    saturated = tuple(
        (int(a) - 1, int(b) - 1)
        for a, b in re.findall(r'S(\d+)-(\d+)', generalization_extention)
    )
    return alkyl, hetro, saturated


def transfer_positions_of_generalization_extention(
    generalization_extention: List[str],
    match: mod.DGVertexMapper.Result.match
    ) -> Tuple[
        List[mod.Graph.Vertex],
        List[Tuple[mod.Graph.Vertex, mod.Graph.Vertex]],
        List[mod.Graph.Vertex]
    ]:
    """Convert generalization extensions to vertices of the graph."""
    alkyl_structures, hetro_structures, saturated_structures = \
        _parse_generalization_positions(generalization_extention)

    alkyl_pos_in_graph = [match[vertex_by_id(match.domain, x)] for x in alkyl_structures]
    hetro_pos_in_graph = [match[vertex_by_id(match.domain, x)] for x in hetro_structures]
    saturated_pos_in_graph = [
        (match[vertex_by_id(match.domain, x[0])], match[vertex_by_id(match.domain, x[1])])
        for x in saturated_structures
        ]

    return alkyl_pos_in_graph, hetro_pos_in_graph, saturated_pos_in_graph


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "transfer_positions_of_generalization_extention",
]
