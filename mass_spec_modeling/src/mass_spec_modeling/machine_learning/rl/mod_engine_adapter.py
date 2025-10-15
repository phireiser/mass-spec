"""Mod Adapter"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import  List, Tuple, Set, Optional
import mod

from mass_spec_modeling.mod_fragmentation import utils

# ------------------------------
# State wrapper for "a given hypergraph"
# ------------------------------
@dataclass
class DGState:
    """
    Wraps a derivation hypergraph (DG) and a current node pointer.
    'dg' can be your MØD Derivation Graph / Hypergraph object.
    We also track which hyperedges were already 'used' to avoid duplicates.
    """
    dg: mod.DG
    mol_graph: mod.Graph
    used_edge_ids: Set[int] = field(default_factory=set)
    node_id: Optional[int] = 0 # root node



# ------------------------------
# Adapter
# ------------------------------
class ModEngineAdapter:
    """
    A thin bridge used by RL envs.
    for a given hypergraph DG
    - list_out_edges(dg, node_id) -> List[int]   # hyperedge ids leaving this node
    - edge_rule_id(dg, edge_id) -> int
    - edge_products(dg, edge_id) -> List[Any]    # product fragment objects
    """

    # ------------------------------
    # Public API expected by the RL env
    # ------------------------------
    def enumerate_applications(self, state: DGState) -> List[int]:
        """
        Return a list of candidate actions for the current state.
        For molecule mode:   [(rule_id, site_info), ...]
        For hypergraph mode: [(edge_id, None), ...]   # we use edge_id as the 'site'
        """

        assert isinstance(state, DGState), "Expected DGState"
        dg, node_id = state.dg, state.node_id
        edge_ids = utils.get_out_edges_by_vertex_id(dg, node_id)  # all outgoing hyperedges
        # Filter out already used edges (prevents duplicates)
        edge_ids = [e for e in edge_ids if e not in state.used_edge_ids]
        # Actions are (edge, None) - RL doesn't need a separate site payload here
        return edge_ids

    def apply(self, edgde_id: int, state: DGState) -> Tuple[bool, List[float]]:
        """
        Execute the selected action.
        Apply.
        Returns: (ok, new_fragment_masses)
        """
        assert isinstance(state, DGState), "Expected DGState"
        if edgde_id in state.used_edge_ids:
            # Trying to reuse an already consumed key: treat as invalid
            return False, []

        # Extract products on that hyperedge and compute masses
        prod_ids: List[int] = utils.get_fragment_ids_by_edge_id(state.dg, edgde_id)  #  fragment ids
        next_node = prod_ids[0]
        assert len([prod_ids])== 1, "should only be one molecule"
        prods = [v.graph for v in state.dg.vertices if v.id in prod_ids]
        if "a(" in prods[0].graphDFS:
            prods = [utils.graph_from_term(g) for g in prods]
        masses = [float(p.exactMass) for p in prods]
        smi = next(p.smiles for p in prods)

        # Mark edge as used in this episode state
        state.used_edge_ids.add(edgde_id)

        # (Optional) advance the pointer to product node(s).
        # If your DG models fragmentation edges as node->set_of_products,
        # you can pick a canonical next node or keep the same node to allow multi-branch expansions.
        # Here we keep the same node_id; the RL reward is based on accumulating fragments anyway.
        return True, masses, next_node, smi


    def preview_masses(self, edge_id: int, state: DGState) -> List[float]:
        """takes an edge_id & returns the masses"""
        prod_ids = utils.get_fragment_ids_by_edge_id(state.dg, edge_id)
        prods = [v.graph for v in state.dg.vertices if v.id in prod_ids]
        if "a(" in prods[0].graphDFS:
            prods = [utils.graph_from_term(g) for g in prods]
        return [float(p.exactMass) for p in prods]

    def preview_smiles(self, edge_id: int, state: DGState) -> str:
        """takes an edge_id & returns the smile of that fragment"""
        prod_ids = utils.get_fragment_ids_by_edge_id(state.dg, edge_id)
        prods = [v.graph for v in state.dg.vertices if v.id in prod_ids]
        if "a(" in prods[0].graphDFS:
            prods = [utils.graph_from_term(g) for g in prods]
        return next(p.smiles for p in prods)
