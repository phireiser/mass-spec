"""
Mapping helpers extracted from rule_extention.
"""
import mod
from .term_transfers import graph_from_term


def get_rule_2_molecule_maps(
    derivation: mod.Derivation,
    label_settings: mod.LabelSettings,
    right_limit: "int | None" = None,
    ) -> "list[mod.DGVertexMapper.Result.match]":
    """Return *all* vertex maps from the rule's left side onto the molecule.

    A single derivation edge can admit more than one embedding of the rule into
    the reactant molecule (molecular symmetry / automorphisms, or genuinely
    distinct matches). ``mod.DGVertexMapper`` yields one ``Result`` per
    embedding; we keep every one so callers can decide how to combine the
    per-match outcomes instead of silently relying on whichever match ``mod``
    happens to produce first (see ``sub_group``).

    ``right_limit`` is forwarded to ``DGVertexMapper``'s ``rightLimit`` argument,
    which caps how many right-side (product-graph automorphism) comaps are
    enumerated per left match. ``None`` (default) leaves mod's own default
    (effectively unbounded) for callers that need every embedding. Callers whose
    result depends only on the *left* map -- e.g. ``sub_group``, which only looks
    at where the rule's generalized positions land in the reactant -- can pass
    ``right_limit=1`` to avoid materialising the full left x right product
    (up to ~10^4 embeddings per derivation) without losing any distinct left
    map. See the call site in ``core/predicates.sub_group`` for the correctness
    argument and validation.
    """
    # The embeddings depend only on this single derivation's left/right graphs
    # and its rule, not on the rest of the database. Seeding the scratch DG with
    # the whole discovered-species database (as this used to) made every call
    # rebuild a DG over all species discovered so far -- quadratic over a run,
    # since this is invoked per derivation from the `sub_group` predicate.
    # Restrict it to the two graphs actually involved. (The former `graphs`
    # parameter was dead once this switched to left/right seeding and has been
    # removed; the caller no longer materialises `dg.graphDatabase` per call.)
    dg_new = mod.DG(
        graphDatabase=[*derivation.left, *derivation.right],
        labelSettings=label_settings,
    )
    with dg_new.build() as b:
        d = mod.Derivation()
        d.left = derivation.left
        d.rule = derivation.rule
        d.right = derivation.right
        b.addDerivation(d)
    e = next(edge for edge in dg_new.edges if derivation.rule in edge.rules)
    vms = mod.DGVertexMapper(e) if right_limit is None \
        else mod.DGVertexMapper(e, True, right_limit)
    return [vm.match for vm in vms]


def get_rule_2_molecule_map(
    derivation: mod.Derivation,
    label_settings: mod.LabelSettings
    ) -> "mod.DGVertexMapper.Result.match | None":
    """Backward-compatible helper returning only the first match (or ``None``).

    Prefer :func:`get_rule_2_molecule_maps` whenever the number of embeddings
    matters; this wrapper exists for callers that only need a single match.
    """
    matches = get_rule_2_molecule_maps(derivation, label_settings)
    return matches[0] if matches else None


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "get_rule_2_molecule_maps",
    "get_rule_2_molecule_map",
]
