"""
predicate definions to be used in strategy
"""

import mod
from .. import utils
from ..rules.migration import (
    CHARGE_MIGRATION_NAME,
    RADICAL_MIGRATION_NAME,
    MIGRATION_RULE_NAMES,
)


def _mem_growth_log(derivation, phase: str, n_matches: int) -> None:
    """Per-derivation memory sampling for --mem-diag (no-op when disabled).

    Samples the process peak-RSS watermark and, only when it GREW, attributes the
    growth to this derivation's rule + reactant mass/charge + embedding fan-out.
    ``phase`` distinguishes the sample taken on entry (``"pre"`` -- captures growth
    from MØD's product construction, before the predicate) from the one after the
    embedding enumeration (``"map"`` -- captures growth from get_rule_2_molecule_maps
    and carries ``n_matches``). The reactant mass/charge are computed only on a
    growth event, so the disabled/steady-state path stays cheap.
    """
    sample = utils.mem_grown()
    if sample is None:
        return
    try:
        mass = round(sum((utils.exact_mass_from_term(g) or 0.0) for g in derivation.left), 2)
        charge = sum(utils.net_charge_from_term(g) for g in derivation.left)
    except Exception:
        mass, charge = -1, -1
    utils.mem_write(sample, phase, derivation.rule.name, mass, charge, n_matches)


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


def migration_profit_gate(strategy: mod.DGStrat) -> mod.rightPredicate:
    """Keep only the *profitable* charge/radical migration hops; pass everything else.

    The fully delocalized charge model lets the charge and radical migrate across the
    whole heavy-atom framework. On unsaturated/heteroatom-dense molecules every hop is
    productive, but on a saturated sigma framework (steroid rings, long alkyl chains)
    the decoration wanders over every C-C bond, producing O(#atoms) charge-position
    isomers that never reach a cleavable site -- the blow-up that makes the large
    saturated tail un-buildable.

    This gate fires ONLY on migration derivations (identified by ``derivation.rule.name``)
    and admits a hop only when the migrated decoration lands on a reactive site
    (:func:`utils.charge_radical_on_reactive_site` -- on/adjacent to unsaturation or a
    heteroatom, i.e. where a fragmentation rule can use it). Ionization and every
    fragmentation derivation pass unconditionally, so the spectrum's fragment-forming
    chemistry is untouched; only wasteful charge-walking is pruned.

    Caveat measured, not a free lunch: "profitable" is not fully knowable without doing
    the downstream cleavage, so this local proxy still drops a hop that *would* have
    enabled a deeper rearrangement.

    **The reactive shell is radius-1, so the gate also blocks TRANSIT hops.** A decoration
    three or more bonds from the nearest heteroatom/unsaturation can never walk to it:
    every intermediate landing site is itself non-reactive, so every hop along the path is
    vetoed. On a *fully* decorated framework (toluene, glucose) that costs nothing -- every
    atom is reactive and the gate is ~a no-op -- but on a partially saturated hetero
    molecule it removes real peaks: cyclohexanol loses m/z 41 (22% rel.) and 43 (14%),
    2-hexanone loses 27 (9%), ethyl acetate loses 74. Since a large saturated interior with
    one or two heteroatoms is exactly the class this gate targets, treat its coverage as
    materially lossy, not merely "deep-cascade" lossy, until a distance-monotone variant
    (admit a hop that does not increase BFS distance to the reactive set) is measured.
    """

    def predicate(d):
        name = d.rule.name
        if name == CHARGE_MIGRATION_NAME:
            want_charge = True
        elif name == RADICAL_MIGRATION_NAME:
            want_charge = False
        else:
            return True  # ionization + fragmentation are never gated
        # Fail OPEN. The reactive-site test parses term labels, and its helpers raise
        # (``parse_term_atom`` asserts, ``decode_edge_label`` raises ValueError) on a label
        # outside the closed term alphabet. An exception raised inside a rightPredicate
        # propagates out of ``dg.build().execute(...)`` and aborts the whole run -- which on
        # this gate's target molecules means destroying a 3-5 hour build over one derivation.
        # No live trigger is known (0/150 rules emit an unbound right-side placeholder), so
        # this is latent insurance; accepting the derivation matches migration's additive
        # default and can only cost DG size, never a peak.
        try:
            return all(
                utils.charge_radical_on_reactive_site(g, want_charge) for g in d.right
            )
        except Exception:
            return True

    return mod.rightPredicate[predicate](strategy)


def migration_multiplicity_cap(
    strategy: mod.DGStrat,
    cap: int,
    parent_vertex_count: "int | None" = None,
    stats: "dict | None" = None,
    ) -> mod.rightPredicate:
    """Admit at most ``cap`` charge/radical placement variants per underlying skeleton.

    This is the cheapest measured way to keep the fully delocalized charge model affordable,
    and the only pruning scheme in this project that is not an instance of the cost/coverage
    coupling. It makes **no claim about which hop is chemically productive** -- that question
    was shown ten times over to be unanswerable locally (a hop pays iff it enables a
    downstream cleavage, knowable only by doing the cleavage). It instead bounds REDUNDANCY,
    and the asymmetry it exploits is measured: MØD's graph database buckets on
    ``(numVertices, numEdges)`` and its per-derivation cost is linear in that bucket's
    population -- hence quadratic in its final size -- while a skeleton contributes exactly
    ONE mass to the spectrum, so the marginal value of its Nth decoration saturates. On
    decalin the mass set stops changing above cap 3 while multiplicity reaches 45: variants
    4..45 of every skeleton cost the quadratic and buy nothing.

    ``parent_vertex_count`` restricts the budget to skeletons with that many vertices -- the
    parent-mass class, which is MØD's dominant ``(n, n)`` + ``(n, n-1)`` buckets and holds
    65-68% of all species. Fragment skeletons stay uncapped. This "spend the budget only
    where the quadratic is" shape measured strictly better than capping everything: decalin
    2883 species / 14.0x fewer isomorphism calls / complete 42-mass set, versus 3374 / 9.0x
    for a global cap 3 at identical coverage. Pass ``None`` to cap every skeleton.

    **Install it OUTERMOST** -- ``migration_multiplicity_cap(charge_bound(amu_bound(...)))``.
    Nested right predicates are evaluated innermost-first and short-circuit on the first
    ``False``, so an accept granted by the outermost predicate cannot be overruled downstream
    and the budget therefore never charges for a derivation that is later discarded.

    Two subtleties the budget accounting depends on, both measured:

    * mod does **not** call the predicate exactly once per derivation -- it presents 1.00-1.12x
      per distinct derivation on symmetric molecules, as several rule embeddings collapse onto
      one product, always back-to-back. Charging per CALL would silently halve the effective
      cap there, so the budget is charged per distinct **product identity**.
    * ``checkIfNew`` runs BEFORE the predicate, so the graph handed over is the one already in
      the database whenever the product is isomorphic to a known species. ``mod.Graph.id`` is
      therefore an exact product identity and a safe memo key (0 conflicts observed over
      12000+ ids), which is what makes the ~100 us skeleton key affordable.

    Note this bounds only MIGRATION-produced variants. Fragmentation and per-site ionization
    are never gated, so the derivation graph legally holds more than ``cap`` variants of a
    skeleton; "at most N variants per skeleton in the DG" would be false.

    **Not safe as a global default.** Losslessness is class-dependent and NOT monotone in
    ``reactive_heavy_fraction``: at cap 3 decalin (rf 0.000) and the aromatics (rf 1.000) lose
    nothing, but cyclohexanol (rf 0.286) loses 5.9% of its NIST intensity and piperidine
    (rf 0.500) loses 26.5% including its second-largest peak, with no useful operating point
    at any cap. The cap is free at both extremes of decoration density and lossy in between,
    because it is an unbiased subsample (verified: decoration-position distributions barely
    move) -- and a uniform subsample suffices only where placements are interchangeable.
    """
    assert cap >= 1, "multiplicity cap must admit at least one variant per skeleton"
    if stats is None:
        stats = {}
    stats.setdefault("accepted", 0)
    stats.setdefault("rejected", 0)
    stats.setdefault("failed_open", 0)
    key_memo: "dict[int, tuple]" = {}
    admitted: "dict[tuple, set]" = {}

    def predicate(d):
        # FAIL OPEN, as in migration_profit_gate: an exception raised inside a rightPredicate
        # propagates out of dg.build().execute() and destroys a multi-hour build. Accepting on
        # error matches migration's additive default -- it can only cost DG size, never a peak.
        try:
            if d.rule.name not in MIGRATION_RULE_NAMES:
                return True  # ionization + fragmentation are never capped
            products = list(d.right)
            identity = tuple(sorted(g.id for g in products))

            keys = []
            for g in products:
                key = key_memo.get(g.id)
                if key is None:
                    key = key_memo[g.id] = utils.skeleton_key(g)
                keys.append(key)
            # A multi-component right side is keyed as ONE composite skeleton so the budget is
            # per hop product rather than per component. Migration is unimolecular and has
            # never produced one, but keying defensively costs nothing.
            key = keys[0] if len(keys) == 1 else tuple(sorted(keys))

            if parent_vertex_count is not None and key[0] != parent_vertex_count:
                return True  # outside the parent-mass class: uncapped

            seen = admitted.setdefault(key, set())
            if identity in seen:
                return True  # duplicate presentation of a variant already paid for
            if len(seen) < cap:
                seen.add(identity)
                stats["accepted"] += 1
                return True
            stats["rejected"] += 1
            return False
        except Exception:
            stats["failed_open"] += 1
            return True

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
        # mem-diag: sample before any work so a growth here is attributed to MØD's
        # product construction for this derivation (runs before the predicate).
        _mem_growth_log(derivation, "pre", -1)

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
            label_settings = derivation_graph.labelSettings,
            right_limit = 1,
        )

        # mem-diag: sample after the embedding enumeration so a growth here is
        # attributed to get_rule_2_molecule_maps, with the fan-out (n_matches) that
        # the C++-cost theory blames.
        _mem_growth_log(derivation, "map", len(matches))

        # No embedding found: keep the previous behaviour of accepting the
        # derivation (the old code fell through the `if match:` block to
        # `return True`).
        if not matches:
            return True

        # There used to be a dedup here, caching `_match_satisfies` on a signature of
        # the match's generalized (R/Y/S) positions. It was worth it when mod handed
        # back ~10^3 embeddings per derivation that mapped those positions to the same
        # atoms. `right_limit=1` removed that multiplicity at the source: what survives
        # are *distinct* left maps, which have distinct signatures, so the cache could
        # only ever miss. Measured over 2011 derivations across 9 molecules (including
        # glucose and the symmetric neopentane/p-xylene), 2003 derivations yield a single
        # match and 8 yield two, and in *zero* of them did two matches share a signature.
        # Evaluate directly; the cache was pure overhead.
        def evaluate(match) -> bool:
            positions = utils.transfer_positions_of_generalization_extention(
                generalization_extention, match
            )
            return _match_satisfies(derivation, match, *positions)

        # Accept the derivation if any embedding satisfies the definition
        # (logical OR -- the chemically correct, existential semantics; see
        # docstring). `require_all_matches` switches to AND for experimentation
        # only. Generators keep the short-circuit: `any` stops at the first
        # satisfying match, `all` at the first failing one.
        results = (evaluate(match) for match in matches)
        return all(results) if require_all_matches else any(results)

    return mod.rightPredicate[predicate](strategy)
