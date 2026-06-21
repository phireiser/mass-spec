"""
predicate definions to be used in strategy
"""

import mod
from .. import utils


def amu_bound(
    strategy: mod.DGStrat,
    minimum: int = 50,
    maximum: int = 500
    ) -> mod.rightPredicate:

    """
    enforces that the fragments are not heavier than max and have more mass than the minimum
    """

    def predicate(derivations):
        masses = []
        for g in derivations.right:
            g = utils.graph_from_term(g)
            if g.isMolecule:
                masses.append(g.exactMass)
        bounds_check = any((mass > minimum) and (mass < maximum) for mass in masses)
        return bounds_check
    return mod.rightPredicate[predicate](strategy)

def charge_bound(
    strategy: mod.DGStrat,
    minimum: int = 0,
    maximum: int = 1
    ) -> mod.rightPredicate:

    """
    enforces that the fragments are staying within a certain charge range
    """

    def predicate(d):
        for g in d.right:
            g = utils.graph_from_term(g)
            if g.isMolecule:
                charge = g.smiles.count('+') - g.smiles.count('-')
                if minimum <= charge <= maximum:
                    return True
        return False
    return mod.rightPredicate[predicate](strategy)


def sub_group(
    strategy: mod.DGStrat,
    derivation_graph: mod.DG,
    require_all_matches: bool = False,
    ) -> mod.rightPredicate:
    """
    uses the rule extention (string after §) to keep make chemical group definitons possible

    A single derivation can embed the rule into the molecule in more than one
    way. ``mod.DGVertexMapper`` already collapses symmetry-equivalent maps
    (``upToIsomorphismGDH`` is on by default), so multiple matches are genuinely
    distinct embeddings -- typically differing only in how the *generalized*
    positions (R/Y/S) are assigned while the reacting core stays fixed.

    We evaluate the subgroup definition against *every* match and accept the
    derivation if **any** embedding satisfies it (logical OR). This is the
    chemically correct semantics: EI-MS fragmentation is existential -- a
    fragment forms as long as *some* substructure supports the pathway, so the
    presence of other, non-qualifying assignments must not veto a valid one.
    Requiring *all* embeddings to qualify would over-filter and drop feasible
    fragments.

    ``require_all_matches=True`` switches to a logical AND over matches; it is
    kept for experimentation only and is not the chemically intended behaviour.
    """

    def _match_satisfies(derivation, match, generalization_extention) -> bool:
        """Evaluate the subgroup definition for a single rule->molecule embedding."""
        alkyl_position, hetro_position, saturated_position = \
            utils.transfer_positions_of_generalization_extention(
                generalization_extention,
                match
            )

        hetro_bool = True
        alkyl_bool = True
        sat_bool = True

        if saturated_position:
            for position in saturated_position:
                satpath = utils.saturated_path(
                    graph = derivation.left,
                    start_vertex = position[0],
                    end_vertex = position[1],
                    allowed_labels = utils.ALK_NES_LABELS,
                    match = match,
                    max_expansions = 20000
                    )

                if not satpath: #  set only false but stay false if true
                    sat_bool = False


        if alkyl_position:
            alkyl_bool = False
            neighbor_labels, _ = utils.collect_bfs(
                graphs = derivation.left,
                start_vertices = alkyl_position,
                match = match,
                max_visits = 5000
            )
            is_subset = set(neighbor_labels).issubset(set(utils.ALK_NES_LABELS))
            if len(set(neighbor_labels)) > 0 and is_subset:
                alkyl_bool = True


        if hetro_position:
            hetro_bool = False
            neighbor_labels, _ = utils.collect_bfs(
                graphs = derivation.left,
                start_vertices = hetro_position,
                match = match,
                max_visits = 5000
            )
            diff = set(neighbor_labels) - set(utils.ALK_NES_LABELS)
            if len(diff) <= 1:
                # not only hetro atoms strictly
                # as the defnition says but, also carbon atoms
                # as McLafferty book is using them as well
                hetro_bool = True


        return sat_bool & alkyl_bool & hetro_bool

    def predicate(derivation):
        rule_parts = derivation.rule.name.split("§")
        generalization_extention = rule_parts[1] if len(rule_parts) > 1 else None

        # no rule extention -> nothing to constrain
        if not generalization_extention:
            return True

        # A derivation edge can have multiple rule->molecule embeddings; fetch
        # them all rather than silently using the first one.
        matches = utils.get_rule_2_molecule_maps(
            derivation = derivation,
            graphs = derivation_graph.graphDatabase,
            label_settings = derivation_graph.labelSettings
        )

        # No embedding found: keep the previous behaviour of accepting the
        # derivation (the old code fell through the `if match:` block to
        # `return True`).
        if not matches:
            return True

        # Accept the derivation if any embedding satisfies the definition
        # (logical OR -- the chemically correct, existential semantics; see
        # docstring). `require_all_matches` switches to AND for experimentation
        # only. Generators keep the short-circuit: `any` stops at the first
        # satisfying match, `all` at the first failing one.
        results = (
            _match_satisfies(derivation, match, generalization_extention)
            for match in matches
        )
        return all(results) if require_all_matches else any(results)

    return mod.rightPredicate[predicate](strategy)
