"""
strategy definition
"""
from typing import List
import utils
from predicates import sub_group, charge_bound, amu_bound
import mod

def make_strategy(
    derivation_graph: mod.DG,
    universe: mod.Graph,
    ionization: List[mod.Rule],
    fragmentation: List[mod.Rule]
    ) -> mod.DGStrat:

    """
    compile a strategy to perform the ionization and fragmentation
    """

    mass = utils.graph_from_term(universe).exactMass

    strategy = (
            mod.addSubset(universe)
        >> 	sub_group(
            mod.repeat[1](ionization),
            derivation_graph
            )
        >>  charge_bound(
                amu_bound(
                    sub_group(
                        mod.repeat[5](fragmentation),
                        derivation_graph
                    ),
                    minimum = 10, #TODO Research what is the actual pupchem-data minimum
                    maximum = mass if mass is not None else 100 #TODO also here: we should not need this ckeck(if)
                )
            )
    )
    return strategy
