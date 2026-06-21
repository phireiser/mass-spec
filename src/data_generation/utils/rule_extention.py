"""
rule extension helper functions
Refactored to delegate diagnostics, mapping, traversal, and label utils.
"""
import re
from typing import List, Tuple
import mod

from .traversal import vertex_by_id


def transfer_positions_of_generalization_extention(
    generalization_extention: List[str],
    match: mod.DGVertexMapper.Result.match
    ) -> Tuple[
        List[mod.Graph.Vertex],
        List[Tuple[mod.Graph.Vertex, mod.Graph.Vertex]],
        List[mod.Graph.Vertex]
    ]:
    """Convert generalization extensions to vertices of the graph."""
    alkyl_structures = re.findall(r'R(\d+)', generalization_extention)
    hetro_structures = re.findall(r'Y(\d+)', generalization_extention)
    saturated_structures = re.findall(r'S(\d+)-(\d+)', generalization_extention)

    alkyl_structures = [int(x) - 1 for x in alkyl_structures]
    hetro_structures = [int(x) - 1 for x in hetro_structures]
    saturated_structures = [(int(x[0])-1, int(x[1])-1)  for x in saturated_structures]

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
