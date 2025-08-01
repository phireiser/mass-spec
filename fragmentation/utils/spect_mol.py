"""
get spectrum from graph
"""
from typing import Set, List, Tuple
import utils
import mod

def get_parent_rules_for_graph(
    derivation_graph: mod.DG,
    search_target_graph: mod.Graph
    ) -> List[int]:

    """
    get all graphs that are used for parent-products of that product
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
    get spectra from mod derivation graph
    """
    spectra = []
    for graph_term in derivation_graph.graphDatabase: # when loading DG len(createdGraphs)=0
        graph = utils.graph_from_term(graph_term)
        if graph.isMolecule:
            if '+' in graph.getGMLString(): # only charged fragments can be detected

                found = False # update spectra list if allready occuring

                rules = set(get_parent_rules_for_graph(derivation_graph,graph_term))

                for i, (mass, occurence, old_rules) in enumerate(spectra):
                    if abs(mass - graph.exactMass) < 1e-2:
                        spectra[i] = (graph.exactMass, occurence + 1, old_rules.union(rules))
                        found = True
                        break
                if not found: # add to spectra list if not occuring
                    spectra.append((graph.exactMass, 1, rules))
        else:
            print(graph.getGMLString())
            raise RuntimeWarning("there are some graphs that are not molecules")
    return spectra
