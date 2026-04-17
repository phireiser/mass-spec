"""
Strategy definitions for forward and backward derivation graph construction.

Notes
- Forward starts from a single universe graph (the molecule term) and applies ionization once
    and fragmentation up to a bounded repeat.
- Backward starts from a list of fragment graphs and applies inverse rules with the same bounds.
"""
from typing import List
import mod
from .predicates import sub_group, charge_bound, amu_bound


def make_fwd_strategy(
    derivation_graph: mod.DG,
    universe: mod.Graph,
    ionization: List[mod.Rule],
    fragmentation: List[mod.Rule],
    max_mass: float = 100,
    min_mass: float = 10,
    frag_repeat: int = 5,
    ) -> mod.DGStrat:

    """
    compile a strategy to perform the ionization and fragmentation
    """

    assert frag_repeat > 0, "fragmentation repeat must be positive."
    assert max_mass > min_mass, "fragmentation max mass must be larger than min mass."

    strategy = (
            mod.addSubset(universe)
		>> 	sub_group(mod.repeat[1](ionization), derivation_graph)
        >>  charge_bound(
                amu_bound(
                    sub_group(mod.repeat[frag_repeat](fragmentation), derivation_graph),
                    minimum = min_mass,  # TODO: consider configuring from dataset stats
                    maximum = max_mass,
                )
            )
    )
    return strategy


def make_bwd_strategy(
    derivation_graph: mod.DG,
    universe: List[mod.Graph],
    fragmentation: List[mod.Rule],
    max_mass: float = 100,
    min_mass: float = 10,
    frag_repeat: int = 5,
    ) -> mod.DGStrat:

    """
    compile a strategy to perform the ionization and fragmentation
    """
    assert frag_repeat > 0, "fragmentation repeat must be positive."
    assert max_mass > min_mass, "fragmentation max mass must be larger than min mass."

    strategy = (
            mod.addSubset(universe)
        >>  charge_bound(
                amu_bound(
                    sub_group(mod.repeat[frag_repeat](fragmentation), derivation_graph),
                    minimum = min_mass,  # TODO: consider configuring from dataset stats
                    maximum = max_mass,
                )
            )
    )
    return strategy
