"""
Charge/radical migration rules for the fully delocalized charge model.

In the *localized* scheme, ionization pins the radical cation to one atom and every
fragmentation rule matches a specific charge/radical position, which forces the ~80
``varN`` / "left-right charge" / charge-shuffle duplicates. The delocalized scheme
instead lets the positive charge and the radical **migrate independently** across the
heavy-atom framework, so one ionization event reaches every reacting site.

These two rules are authored *directly in term-mode GML* (``a(Symbol, Charge, Radical)``
vertices, ``e(Order)`` bonds -- the same encoding
:func:`data_generation.utils.term_transfers.term_from_graph` emits) rather than via the
DFS ``mod.Rule.fromDFS`` path, because that path cannot express what migration needs and
the term path can (verified against mod 1.0.0):

* **Independent element variables** ``_A`` / ``_B`` -- ``encode_vertex_label`` collapses
  every DFS placeholder to the single variable ``_A``, forcing both atoms to the same
  element; distinct names authored in GML stay independent, so charge can hop C->O, O->C,
  any heavy pair.
* **A radical-slot variable** (``_R`` / ``_S``) that binds any radical count and is carried
  through unchanged, so a *charge* hop leaves the radical where it is (and vice versa) --
  this is what makes the two migrations independent.
* **A bond-order variable** ``e(_X)`` that matches single/double/triple **and** aromatic
  ``e(ar)`` in one rule, preserving the bond term. Because it preserves ``e(ar)`` rather
  than picking a Kekule form, it does not reintroduce the resonance-dependence that the
  curated aromatic rules avoid.

The ``constrainLabelAny`` blocks restrict ``_A``/``_B`` to the molecule's occurring heavy
atoms so charge/radical never lands on hydrogen -- an ``a(H, 1, ...)`` bridging proton /
``a(H, 0, 1)`` H-radical is chemically spurious and only inflates the DG. ``mod`` has no
``constrainLabelNone`` (allowlist only), so the caller passes the heavy-atom allowlist.

Migration conserves atoms, charge and spin (it moves one ``+`` or one ``.`` across an
unchanged bond), so it is chemically exempt from the fragmentation conservation guard; it is
kept in its own list, not ``fragmentation``. Note the guard could not actually *verify* that:
``rules/__init__.py._conservation_defect`` parses string-mode labels and reads the term labels
``a(_A, 1, _R)`` / ``a(_B, 0, _S)`` as opaque atom symbols, so it reports an ``'atoms'`` defect
for both rules. That is latent (the guard never sees them) but means these rules must stay out
of ``fragmentation`` unless the guard learns term labels.
"""
from typing import List
import mod


# Rule names, kept as module constants so the profit gate (predicates.py) can
# recognise a migration derivation by ``derivation.rule.name`` without hard-coding
# the strings at the use site. ``build_migration_rules`` names its rules with these.
CHARGE_MIGRATION_NAME = "charge migration"
RADICAL_MIGRATION_NAME = "radical migration"
MIGRATION_RULE_NAMES = frozenset({CHARGE_MIGRATION_NAME, RADICAL_MIGRATION_NAME})


def _constrain_label_any(labels: List[str], placeholder: str) -> str:
    """A ``constrainLabelAny`` block restricting term variable ``_<placeholder>`` to
    ``labels``. Inlined (not imported from utils) so the rules package keeps no import
    dependency on utils, matching the convention in this package's ``__init__``.
    """
    quoted = " ".join(f'label "{x}"' for x in labels)
    return f'\n    constrainLabelAny [ label "_{placeholder}" labels [ {quoted} ] ]'


# Term-GML templates. ``%s`` is replaced by the per-molecule heavy-atom constraint blocks.
# The migrating decoration lives in left/right (it changes); the bond and the preserved
# slots (element _A/_B, the non-migrating decoration _R/_S or _C/_D) are variables that
# unify left<->right so they are carried through unchanged.
_CHARGE_HOP_GML = """rule [
    left  [ node [ id 0 label "a(_A, 1, _R)" ] node [ id 1 label "a(_B, 0, _S)" ] ]
    context [ edge [ source 0 target 1 label "e(_X)" ] ]
    right [ node [ id 0 label "a(_A, 0, _R)" ] node [ id 1 label "a(_B, 1, _S)" ] ]%s
]"""

_RADICAL_HOP_GML = """rule [
    left  [ node [ id 0 label "a(_A, _C, 1)" ] node [ id 1 label "a(_B, _D, 0)" ] ]
    context [ edge [ source 0 target 1 label "e(_X)" ] ]
    right [ node [ id 0 label "a(_A, _C, 0)" ] node [ id 1 label "a(_B, _D, 1)" ] ]%s
]"""


def build_migration_rules(heavy_atoms: List[str]) -> List[mod.Rule]:
    """Build the (charge-hop, radical-hop) term-mode migration rules for a molecule.

    ``heavy_atoms`` is the molecule's occurring heavy elements (undecorated symbols, no
    ``H``) -- typically ``sorted(all_occuring([mol], ALL_ATOMS) - {"H"})``. Returns ``[]``
    when there is nothing to migrate across (fewer than the single element needed), so a
    hydrogen-only universe is a no-op rather than an invalid empty ``constrainLabelAny``.
    """
    labels = sorted(set(heavy_atoms) - {"H"})
    if not labels:
        return []
    constraint = _constrain_label_any(labels, "A") + _constrain_label_any(labels, "B")
    charge_hop = mod.Rule.fromGMLString(
        _CHARGE_HOP_GML % constraint, name=CHARGE_MIGRATION_NAME, add=False
    )
    radical_hop = mod.Rule.fromGMLString(
        _RADICAL_HOP_GML % constraint, name=RADICAL_MIGRATION_NAME, add=False
    )
    return [charge_hop, radical_hop]


__all__ = [
    "build_migration_rules",
    "CHARGE_MIGRATION_NAME",
    "RADICAL_MIGRATION_NAME",
    "MIGRATION_RULE_NAMES",
]
