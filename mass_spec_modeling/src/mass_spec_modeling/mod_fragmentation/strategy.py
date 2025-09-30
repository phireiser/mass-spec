"""
strategy definition
"""
from typing import List
import mod
from .predicates import sub_group, charge_bound, amu_bound


def make_fwd_strategy(
    derivation_graph: mod.DG,
    universe: mod.Graph,
    ionization: List[mod.Rule],
    fragmentation: List[mod.Rule],
    max_mass: float = 100
    ) -> mod.DGStrat:

    """
    compile a strategy to perform the ionization and fragmentation
    """

    strategy = (
            mod.addSubset(universe)
        >> 	sub_group(mod.repeat[1](ionization), derivation_graph)
        >>  charge_bound(
                amu_bound(
                    sub_group(mod.repeat[5](fragmentation), derivation_graph),
                    minimum = 10, #TODO find out what is the actual minimum in the source data
                    maximum = max_mass
                )
            )
    )
    return strategy


def make_bwd_strategy(
    derivation_graph: mod.DG,
    universe: List[mod.Graph],
    fragmentation: List[mod.Rule],
    max_mass: float = 100
    ) -> mod.DGStrat:

    """
    compile a strategy to perform the ionization and fragmentation
    """

    strategy = (
            mod.addSubset(universe)
        >>  charge_bound(
                amu_bound(
                    sub_group(mod.repeat[5](fragmentation), derivation_graph),
                    minimum = 10, #TODO find out what is the actual minimum in the source data
                    maximum = max_mass
                )
            )
    )
    return strategy
