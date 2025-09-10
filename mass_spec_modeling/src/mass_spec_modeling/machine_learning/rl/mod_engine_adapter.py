"""Mod Adapter"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Tuple, Optional, Set, Callable, Dict
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
    node_id: int = 0 # root node
    used_edge_ids: Set[int] = field(default_factory=set)

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
    def __init__(
        self,
        list_out_edges: Optional[Callable[[Any, int], List[int]]] = None,
        edge_rule_id: Optional[Callable[[Any, int], int]] = None,
        edge_products: Optional[Callable[[Any, int], List[Any]]] = None,
    ):

        self._list_out_edges  = list_out_edges
        self._edge_rule_id    = edge_rule_id
        self._edge_products   = edge_products

        if any(
            h is None for h in (
                self._list_out_edges,
                self._edge_rule_id,
                self._edge_products)
            ):
            raise ValueError("requires callables")

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
        edge_ids = self._list_out_edges(dg, node_id)  # all outgoing hyperedges
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
        prod_ids: List[int] = self._edge_products(state.dg, edgde_id)  #  fragment ids
        next_node = prod_ids[0]
        assert len([prod_ids])== 1, "should only be one molecule"
        prods = [v.graph for v in state.dg.vertices if v.id in prod_ids]
        if "a(" in prods[0].graphDFS:
            prods = [utils.graph_from_term(g) for g in prods]
        masses = [float(p.exactMass) for p in prods]

        # Mark edge as used in this episode state
        state.used_edge_ids.add(edgde_id)

        # (Optional) advance the pointer to product node(s).
        # If your DG models fragmentation edges as node->set_of_products,
        # you can pick a canonical next node or keep the same node to allow multi-branch expansions.
        # Here we keep the same node_id; the RL reward is based on accumulating fragments anyway.
        return True, masses, next_node


    def preview_masses(self, key: int, state: DGState) -> list[float]:
        prod_ids = self._edge_products(state.dg, key)
        prods = [v.graph for v in state.dg.vertices if v.id in prod_ids]
        if "a(" in prods[0].graphDFS:
            prods = [utils.graph_from_term(g) for g in prods]
        return [float(p.exactMass) for p in prods]


######################## ---------- Backward (assembly) Adapter ----------


@dataclass
class AssemblyState:
    """
    Minimal state for backward molecule assembly.
    G:    your current molecule/graph object being built
    used_action_ids: optional tracking to prevent repeats (depends on adapter semantics)
    steps: number of applied actions so far
    """
    G: Any
    used_action_ids: Set[int] = field(default_factory=set)
    steps: int = 0


class AssemblerAdapter:
    """
    Adapter interface the BackwardMolEnv expects.
    Implement these in your codebase and pass an instance to BackwardMolEnv.

    Required:
      build_initial_graph(seed) -> Any
      enumerate_action_keys(state: AssemblyState) -> List[int]
      preview_masses(action_key: int, state: AssemblyState) -> List[float]
      apply(action_key: int, state: AssemblyState) -> Tuple[bool, List[float], Dict[str, Any]]
          - returns (ok, new_fragment_masses, info)
      is_terminal(state: AssemblyState) -> bool
    """
    def build_initial_graph(self, seed: Optional[Any]) -> Any:
        raise NotImplementedError

    def enumerate_action_keys(self, state: AssemblyState) -> List[int]:
        raise NotImplementedError

    def preview_masses(self, action_key: int, state: AssemblyState) -> List[float]:
        raise NotImplementedError

    def apply(self, action_key: int, state: AssemblyState) -> Tuple[bool, List[float], Dict[str, Any]]:
        raise NotImplementedError

    def is_terminal(self, state: AssemblyState) -> bool:
        raise NotImplementedError

