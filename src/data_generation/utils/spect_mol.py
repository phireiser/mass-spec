"""
Get spectrum from a MOD derivation graph.
"""
from typing import Set, List, Tuple
import mod
from .term_transfers import graph_from_term

def get_parent_rules_for_graph(
    derivation_graph: mod.DG,
    search_target_graph: mod.Graph
    ) -> List[int]:
    """
    Get all rule IDs that are used as parents (precursors) of the given product graph.
    """
    parent_rules = []
    visited = set()
    stack = [search_target_graph]

    while stack:
        current_graph = stack.pop()
        # Avoid reprocessing the same graph
        if current_graph in visited:
            continue
        visited.add(current_graph)
        edges = derivation_graph.findVertex(current_graph).inEdges
        for edge in edges:
            for rule in edge.rules:
                parent_rules.append(rule.id)

            for source in edge.sources:
                stack.append(source.graph)

    return parent_rules


def get_spectra_from_mod_derivation_graph(
    derivation_graph: mod.DG
    ) -> List[Tuple[float, int, Set[int]]]:
    """
    Get spectra from a MOD derivation graph.
    """
    spectra = []
    for graph_term in derivation_graph.graphDatabase:  # Note: when loading DG, len(createdGraphs) == 0
        graph = graph_from_term(graph_term)
        if graph.isMolecule:
            if '+' in graph.getGMLString():  # Only charged fragments can be detected
                found = False  # Update spectra list if already occurring
                rules = set(get_parent_rules_for_graph(derivation_graph,graph_term))

                for i, (mass, occurrence, old_rules) in enumerate(spectra):
                    if abs(mass - graph.exactMass) < 1e-2:
                        spectra[i] = (graph.exactMass, occurrence + 1, old_rules.union(rules))
                        found = True
                        break
                if not found:  # Add to spectra list if not occurring
                    spectra.append((graph.exactMass, 1, rules))
        else:
            print(graph.getGMLString())
            raise RuntimeWarning("There are graphs that are not molecules.")
    return spectra
