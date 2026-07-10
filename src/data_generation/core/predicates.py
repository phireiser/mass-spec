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
        # Compute each fragment's exact mass straight from its term labels
        # instead of round-tripping through a string-mode molecule. `None`
        # means a non-molecule (placeholder atoms), matching the old
        # `if g.isMolecule` guard. Return on the first in-bounds fragment.
        for g in derivations.right:
            mass = utils.exact_mass_from_term(g)
            if mass is not None and minimum < mass < maximum:
                return True
        return False
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
        # Net charge is the sum of per-atom formal charges, which we read
        # straight from the term labels. This replaces the old
        # `graph_from_term(g).smiles.count('+')-count('-')`, which canonicalised
        # a SMILES string per fragment purely to count charge signs. The old
        # `isMolecule` guard only existed because `.smiles` errors on
        # non-molecules; summing term charges never errors, so it is dropped.
        for g in d.right:
            charge = utils.net_charge_from_term(g)
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

    def _positions_signature(alkyl_position, hetro_position, saturated_position):
        """Order-stable identity of a match's *generalized* positions (R/Y/S).

        Within one derivation the morphism (``match.codomain``) is identical for
        every match, and neither ``collect_bfs`` (which ignores ``match``) nor
        ``saturated_path`` (which uses ``match`` only via that constant morphism)
        depends on anything else, so ``_match_satisfies`` is a pure function of
        where the rule's generalized positions land in the molecule. mod hands
        back ~10^3 matches per derivation dominated by symmetry-equivalent
        embeddings that map those positions to the *same* atoms; deduping on this
        signature runs the expensive traversal once per distinct assignment.
        """
        return (
            tuple(v.id for v in alkyl_position),
            tuple(v.id for v in hetro_position),
            tuple((a.id, b.id) for a, b in saturated_position),
        )

    def _match_satisfies(derivation, match, alkyl_position, hetro_position,
                         saturated_position) -> bool:
        """Evaluate the subgroup definition for a single rule->molecule embedding."""
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
        #
        # `right_limit=1` caps `DGVertexMapper`'s enumeration of *right-side*
        # (product-graph automorphism) comaps to one per left match. Unbounded,
        # mod returns the full product of left-match x right-comatch embeddings --
        # up to ~10^4 per derivation on symmetric molecules -- but the subgroup
        # outcome depends only on the *left* map (where the generalized R/Y/S
        # positions land in the reactant), which the right-side multiplicity does
        # not change. So capping it cannot drop a distinct
        # `(alkyl, hetero, saturated)` signature, only redundant repeats of one.
        # Validated byte-identical forward+backward dumps across benzene, toluene,
        # acetone, 1-/2-propanol, 1-butene, acetic acid, propanal and alanine;
        # this is the dominant per-molecule speedup (up to ~13x on 2-propanol),
        # cutting both the native mapper enumeration and the per-match Python
        # signature loop at the source.
        matches = utils.get_rule_2_molecule_maps(
            derivation = derivation,
            graphs = derivation_graph.graphDatabase,
            label_settings = derivation_graph.labelSettings,
            right_limit = 1,
        )

        # No embedding found: keep the previous behaviour of accepting the
        # derivation (the old code fell through the `if match:` block to
        # `return True`).
        if not matches:
            return True

        # `right_limit=1` already collapses the symmetry-equivalent embeddings
        # upstream, so `matches` is now typically one per distinct generalized-
        # position assignment. The signature dedup below is kept as a cheap
        # belt-and-suspenders for any residual multiplicity: within this
        # derivation the morphism is fixed, so the subgroup outcome depends only
        # on that assignment -- run the (expensive) traversal once per distinct
        # signature.
        sig_cache: "dict[tuple, bool]" = {}

        def evaluate(match) -> bool:
            positions = utils.transfer_positions_of_generalization_extention(
                generalization_extention, match
            )
            sig = _positions_signature(*positions)
            cached = sig_cache.get(sig)
            if cached is not None:
                return cached
            result = _match_satisfies(derivation, match, *positions)
            sig_cache[sig] = result
            return result

        # Accept the derivation if any embedding satisfies the definition
        # (logical OR -- the chemically correct, existential semantics; see
        # docstring). `require_all_matches` switches to AND for experimentation
        # only. Generators keep the short-circuit: `any` stops at the first
        # satisfying match, `all` at the first failing one.
        results = (evaluate(match) for match in matches)
        return all(results) if require_all_matches else any(results)

    return mod.rightPredicate[predicate](strategy)
