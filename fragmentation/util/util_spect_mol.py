
from typing import Set, List, Tuple

def getParentRulesForGraph(
    derivationGraph: mod.DG, 
    search_target_graph: mod.Graph
    ) -> List[int]:
    parentRules = []
    visited = set()
    stack = [search_target_graph]

    while stack:
        current_graph = stack.pop()

        # Avoid reprocessing the same graph
        if id(current_graph) in visited:
            continue
        visited.add(id(current_graph))

        try:
            edges = derivationGraph.findVertex(current_graph).inEdges
        except:
            print("Fragment does not exist in DG")
            continue

        for edge in edges:
            try:
                for rule in edge.rules:
                    parentRules.append(rule.id)
            except:
                print("edge exeption in getPartenRulesFromGraph")
                continue

            try:
                for source in edge.sources:
                    stack.append(source.graph)
            except mod.LogicError:
                print("mod logic Error")
                #TODO why?
                continue

    return parentRules


def getSpectraFromMoelDerivationGraph(
    derivationGraph: mod.DG
    ) -> List[Tuple[float, int, Set[int]]]:
    spectra = list()
    sourceGraph = derivationGraph.graphDatabase[0]
    
    for graph_term in derivationGraph.createdGraphs:     
        graph = graphFromTerm(graph_term)
        if graph.isMolecule:
                if '+' in graph.getGMLString(): # only charged fragments can be detected
                        found = False # update spectra list if allready occuring
                        
                        rules = set(getParentRulesForGraph(derivationGraph,graph_term))

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