"""
Mapping helpers extracted from rule_extention.
"""
import mod
from .term_transfers import graph_from_term


def get_rule_2_molecule_maps(
    derivation: mod.Derivation,
    graphs: mod.Graph,
    label_settings: mod.LabelSettings
    ) -> "list[mod.DGVertexMapper.Result.match]":
    """Return *all* vertex maps from the rule's left side onto the molecule.

    A single derivation edge can admit more than one embedding of the rule into
    the reactant molecule (molecular symmetry / automorphisms, or genuinely
    distinct matches). ``mod.DGVertexMapper`` yields one ``Result`` per
    embedding; we keep every one so callers can decide how to combine the
    per-match outcomes instead of silently relying on whichever match ``mod``
    happens to produce first (see ``sub_group``).
    """
    dg_new = mod.DG(graphDatabase = graphs, labelSettings = label_settings)
    with dg_new.build() as b:
        d = mod.Derivation()
        d.left = derivation.left
        d.rule = derivation.rule
        d.right = derivation.right
        b.addDerivation(d)
    e = next(edge for edge in dg_new.edges if derivation.rule in edge.rules)
    vms = mod.DGVertexMapper(e)
    return [vm.match for vm in vms]


def get_rule_2_molecule_map(
    derivation: mod.Derivation,
    graphs: mod.Graph,
    label_settings: mod.LabelSettings
    ) -> "mod.DGVertexMapper.Result.match | None":
    """Backward-compatible helper returning only the first match (or ``None``).

    Prefer :func:`get_rule_2_molecule_maps` whenever the number of embeddings
    matters; this wrapper exists for callers that only need a single match.
    """
    matches = get_rule_2_molecule_maps(derivation, graphs, label_settings)
    return matches[0] if matches else None


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "get_rule_2_molecule_maps",
    "get_rule_2_molecule_map",
]
