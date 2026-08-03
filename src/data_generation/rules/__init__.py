"""
Fragmentation and ionization rules for mass spectrometry.
"""

# Import specific rule collections (not wildcard)
from .benzylAllyl_ringGeneral import (
    benzylAllyl_ionizaton,
    benzylAllyl_fragmentation,
)
from .dehydration import dehydration_all
from .deprotonation import deProtonation_all, ei_molecular_ion, heteroatom_ionization
from .IMS_bookCover import (
    IMS_cover_fragmentation,
    rearrangements,
)
from .IMS_chap4_examples import IMS_chap4_examples
from .IMS_chap8_examples import IMS_chap8_examples
from .wikipedia import (
    wiki_ionization,
    wiki_fragmentation,
)
from .aromatic_ring_loss import aromatic_ring_loss_fragmentation
from .migration import (
    build_migration_rules,
    CHARGE_MIGRATION_NAME,
    RADICAL_MIGRATION_NAME,
    MIGRATION_RULE_NAMES,
)

# TODO benzofuran forming fission (BFF)
# TODO quinone methide (QM) fission
# (heterocyclic ring fission: partially covered by aromatic_ring_loss HCN/CO channels)

ionization = []
ionization.append(ei_molecular_ion)
ionization.extend(heteroatom_ionization)   # O/N/S/... n-electron ionization; see deprotonation.py
ionization.extend(benzylAllyl_ionizaton)
ionization.extend(wiki_ionization)
ionization.extend(deProtonation_all)

fragmentation = []
fragmentation.extend(benzylAllyl_fragmentation)
# fragmentation.extend(deProtonation_all) # hardly probable
fragmentation.extend(dehydration_all)  # intramolecular replacement for the bimolecular IMS_4_28_1
fragmentation.extend(IMS_cover_fragmentation)
fragmentation.extend(IMS_chap4_examples)
fragmentation.extend(IMS_chap8_examples)
fragmentation.extend(wiki_fragmentation)
fragmentation.extend(aromatic_ring_loss_fragmentation)


# ---------------------------------------------------------------------------
# Conservation guardrail for fragmentation rules.
#
# A fragmentation is a rewrite of ONE species into its fragments. Because mod's
# ``rule.right`` holds every product graph, a physically valid fragmentation
# conserves, from left to right, the atom multiset, the total formal charge and the
# total number of unpaired electrons -- the split moves them between fragments, it
# never creates or destroys them.
#
# An audit found ~27 hand-authored rules in IMS_chap4/8_examples that violate this:
# inductive cleavages that leave BOTH fragments charged (charge 1 -> 2, so the
# product is a di-cation that ``charge_bound`` rejects anyway), rules built on
# unphysical bi-/tri-radical placeholders (``Cl..``), one with a literal DFS parse
# error, and several that invent or annihilate an unpaired electron. Measured on a
# 10-molecule sample they account for only 0.9% of surviving charged fragments (2 of
# 229), and those two are themselves non-conserving, i.e. spurious -- so dropping
# them is essentially free and strictly removes chemically impossible species.
#
# Fixing each properly means re-deriving it from its book equation (Gl. 4.23, 8.5,
# ...) -- real chemistry work, tracked separately -- and rushing 27 such rewrites is
# exactly the mis-encoding this cleanup is undoing. So instead of deleting them by
# hand (fragile, and it would drift), this guard drops the non-conserving rules at
# assembly time and names them, and it keeps doing so for any rule added later.
#
# Ionization rules are exempt: forming M+. or losing H./H+ legitimately changes
# charge and spin. The guard runs on the fragmentation list only.

def _label_charge_spin(string_label: str):
    """(undecorated symbol, formal charge, unpaired count) from a mod vertex label.

    Mirrors utils.term_transfers.encode_vertex_label; inlined so this package keeps
    no import dependency on utils just for a guard that runs at import time.
    """
    i = 0
    while i < len(string_label) and string_label[i] not in "+-.":
        i += 1
    symbol, deco = string_label[:i], string_label[i:]
    return symbol, deco.count("+") - deco.count("-"), deco.count(".")


def _conservation_defect(rule):
    """Return a short reason string if ``rule`` fails L->R conservation, else None."""
    def tally(graph):
        charge = spin = 0
        atoms: "dict[str, int]" = {}
        for v in graph.vertices:
            sym, ch, ra = _label_charge_spin(v.stringLabel)
            charge += ch
            spin += ra
            atoms[sym] = atoms.get(sym, 0) + 1
        return charge, spin, atoms

    lc, ls_, la = tally(rule.left)
    rc, rs, ra = tally(rule.right)
    reasons = []
    if la != ra:
        reasons.append("atoms")
    if lc != rc:
        reasons.append(f"charge {lc}->{rc}")
    if ls_ != rs:
        reasons.append(f"spin {ls_}->{rs}")
    return ", ".join(reasons) if reasons else None


def _drop_nonconserving(rules_list):
    """Partition into (kept, dropped[(name, reason)]) by L->R conservation."""
    kept, dropped = [], []
    for r in rules_list:
        defect = _conservation_defect(r)
        if defect is None:
            kept.append(r)
        else:
            dropped.append((r.name, defect))
    return kept, dropped


fragmentation, _dropped_nonconserving = _drop_nonconserving(fragmentation)
if _dropped_nonconserving:
    import sys as _sys
    print(
        f"[rules] conservation guard dropped {len(_dropped_nonconserving)} "
        f"non-conserving fragmentation rule(s); re-author from the book to restore:",
        file=_sys.stderr,
    )
    for _name, _reason in _dropped_nonconserving:
        print(f"[rules]   - {_name}  [{_reason}]", file=_sys.stderr)

__all__ = [
    "ionization",
    "fragmentation",
    # Individual rule collections
    "benzylAllyl_ionizaton",
    "benzylAllyl_fragmentation",
    "dehydration_all",
    "deProtonation_all",
    "ei_molecular_ion",
    "heteroatom_ionization",
    "IMS_cover_fragmentation",
    "IMS_chap4_examples",
    "IMS_chap8_examples",
    "wiki_ionization",
    "wiki_fragmentation",
    "rearrangements",
    "aromatic_ring_loss_fragmentation",
    "build_migration_rules",
    "CHARGE_MIGRATION_NAME",
    "RADICAL_MIGRATION_NAME",
    "MIGRATION_RULE_NAMES",
]
