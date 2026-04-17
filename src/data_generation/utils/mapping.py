"""
Mapping helpers extracted from rule_extention.
"""
import mod
from .term_transfers import graph_from_term


def get_rule_2_molecule_map(
    derivation: mod.Derivation,
    graphs: mod.Graph,
    label_settings: mod.LabelSettings
    ) -> "mod.DGVertexMapper.Result.match | None":
    dg_new = mod.DG(graphDatabase = graphs, labelSettings = label_settings)
    with dg_new.build() as b:
        d = mod.Derivation()
        d.left = derivation.left
        d.rule = derivation.rule
        d.right = derivation.right
        b.addDerivation(d)
    e = next(edge for edge in dg_new.edges if derivation.rule in edge.rules)
    vms = mod.DGVertexMapper(e)
    m = next(iter(vms), None)
    if m is None:
        return None
    return m.match
