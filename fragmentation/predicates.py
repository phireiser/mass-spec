"""
predicate definions to be used in strategy
"""
from utils import *
import mod


def amu_bound(
    strategy: mod.DGStrat,
    minimum: int = 50,
    maximum: int = 500
    ) -> mod.rightPredicate:

    def predicate(derivations):
        masses = []
        for g in derivations.right:
            g = graphFromTerm(g)
            if g.isMolecule:
                masses.append(g.exactMass)
        boundsckeck = any([(mass > minimum) and (mass < maximum) for mass in masses])
        return boundsckeck
    return mod.rightPredicate[predicate](strategy)

def charge_bound(
    strategy: mod.DGStrat,
    minimum: int = 0,
    maximum: int = 1
    ) -> mod.rightPredicate:

    """
    enforces that the fragments are not heaviner then max and have more mass than the minium
    """

    def predicate(d):
        for g in d.right:
            g = graphFromTerm(g)
            if g.isMolecule:
                charge = g.smiles.count('+') - g.smiles.count('-')
                if minimum <= charge <= maximum:
                    return True
        return False
    return mod.rightPredicate[predicate](strategy)


def sub_group(
    strategy: mod.DGStrat,
    derivation_graph: mod.DG
    ) -> mod.rightPredicate:
    """
    uses the rule extention (string after §) to keep make chemical group definitons possible
    """

    def predicate(derivation):
        rule_parts = derivation.rule.name.split("§")
        generalization_extention = rule_parts[1] if len(rule_parts) > 1 else None

        # if any extention
        if generalization_extention:
            match = getRule2MoleculeMap(
                derivation = derivation,
                graphs = derivation_graph.graphDatabase,
                labelSettings = derivation_graph.labelSettings
            )
            if match:
                alkyl_position, hetro_position, saturated_position = \
                    transferPositionsOfGeneralizationExtention(generalization_extention, match)

                hetro_bool = True
                alkyl_bool = True
                sat_bool = True

                if saturated_position:
                    for position in saturated_position:
                        satpath = saturatedPath(
                            graph = derivation.left,
                            start_vertex = position[0],
                            end_vertex = position[1],
                            allowed_labels = alk_nes_lables,
                            match = match
                            ) #TODO could contain multiple matches, really? -> ask Flamm
                        if not satpath: #  set only false but stay false if true
                            sat_bool = False


                if alkyl_position:
                    alkyl_bool = False
                    neighbor_labels, _ = collect_bfs(
                        graphs = derivation.left,
                        start_vertices = alkyl_position,
                        match = match
                    )
                    is_subset = set(neighbor_labels).issubset(set(alk_nes_lables))
                    if len(set(neighbor_labels)) > 0 and is_subset:
                        alkyl_bool = True


                if hetro_position:
                    hetro_bool = False
                    neighbor_labels, _ = collect_bfs(
                        graphs = derivation.left,
                        start_vertices = hetro_position,
                        match = match
                    )
                    diff = set(neighbor_labels) - set(alk_nes_lables)
                    if len(diff) <= 1:
                        # not only hetro atoms strictly
                        # as the defnition says but, also carbon atoms
                        # as McLafferty book is using them as well
                        hetro_bool = True


                return sat_bool & alkyl_bool & hetro_bool
        return True # if there is no rule extention
    return mod.rightPredicate[predicate](strategy)
