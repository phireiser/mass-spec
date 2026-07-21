"""
Intramolecular water elimination (dehydration).

Why this exists
---------------
Loss of H2O is one of the most common EI rearrangements for alcohols, acids and
sugars. Before this module the rule library had NO dehydration rule at all: the
only route to a water loss was the two-step chemical-ionization pair

    IMS_4_28_1:  [_A][O][H] . [H+]        >> [_A][O+]([H])([H])      (protonation)
    IMS_4_28_2:  [_A][O+]([H])([H])       >> [_A+] . [O]([H])([H])   (water loss)

whose first step is BIMOLECULAR -- it consumes a *free* [H+] (minted by
``deProtonation_proton``) and therefore pairs two independent fragments. In a
loaded forward DG that shows up as a multi-source hyperedge, and it accounted for
100% (1494/1494) of all fusion edges in the 127-molecule corpus. A free proton
adding to a fragment is chemical-ionization chemistry, not EI: in EI the molecular
ion fragments in isolation, so the H that leaves with the water must come from
*within the same ion*.

This rule encodes that intramolecular route directly, in a single connected
component, so no free proton and no fragment fusion is needed:

    H-Cb-Ca-O-H   ->   Cb=Ca  +  H2O

i.e. the hydroxyl oxygen leaves together with a hydrogen taken from the adjacent
(beta) carbon, and the resulting Cb-Ca bond becomes a double bond. Atom, charge
and unpaired-electron counts are all unchanged by construction (the rule mentions
no charge and no radical), so it applies equally to a radical cation, an
even-electron cation, or a neutral, leaving whatever charge/radical the species
carries elsewhere untouched -- exactly the behaviour of a real water loss.

Worked check (succinic acid, the corpus's worst fusion-dependent case): the
unimolecularly reachable m/z 73 ion HOOC-CH2-CH2+ matches H-Cb-Ca-O-H with Ca =
the carboxyl carbon, giving O=C=CH-CH2+ + H2O = m/z 55, the experimental base
peak. Previously m/z 55 was reachable ONLY through the bimolecular protonation.
"""

import mod


# beta (1,2) elimination of water from a CARBOXYL group: the leaving -OH sits on a
# carbon that also carries a =O, and the hydrogen comes from the adjacent carbon.
#
# Why restricted to the carboxyl rather than any hydroxyl: the unrestricted
# "[H][C][C][O][H]" form is chemically correct but combinatorially disastrous on
# polyols. A hexose offers a matching H-C-C-O-H at nearly every ring position, so the
# rule fires everywhere and each product still has 4 more hydroxyls to dehydrate;
# measured on glucose/mannose it inflated the DG 341 -> 1571 edges (~26 min builds)
# while raising legitimate coverage only 1.2-1.3x and never reaching the real m/z 73
# base peak (which comes from ring cleavage, not dehydration). The productive
# reaction in every validated case (succinic m/z 55, glutamate m/z 84) lost the
# CARBOXYL oxygen, and sugars have no carboxyl at all -- so requiring the =O both
# keeps the wins and removes the blow-up by construction.
#
# NOTE: this deliberately gives up plain alcohol dehydration (R-OH -> alkene + H2O),
# which is a real EI process. It is deferred, not denied: it needs a gate that limits
# it on polyols (ideally "only on a charged fragment", which MOD cannot express as a
# local rule constraint) before it can be re-enabled.
dehydration_carboxyl = mod.Rule.fromDFS(
    s=
    "[H]1[C]2[C]3({=}[O]6)[O]4[H]5"
    ">>"
    "[C]2{=}[C]3({=}[O]6)"
    "."
    "[O]4([H]5)([H]1)",
    name=
    # NO "§..." generalization extension: every atom here is an explicit C/O/H, so
    # there are no generalized R/Y/S positions to constrain, and `sub_group`
    # short-circuits to True when the name contains no "§". (An earlier "§S2-3"
    # here declared a *saturated path* between the two carbons -- exactly the bond
    # this rule converts into a double bond -- so the predicate vetoed every
    # embedding and the rule silently never fired.)
    "intramolecular water elimination (carboxyl)"
)


# ----------------------------------------------------------------- ortho effect
# Water loss where the hydrogen is donated by a neighbouring *hydroxyl* rather than a
# C-H: the classic "ortho effect" of 2-hydroxy benzoic acids. The phenolic O-H hands
# its hydrogen to the carboxyl -OH, which departs as water, and the phenolic oxygen
# closes onto the carboxyl carbon (a lactone-type ring fused to the arene).
#
#     HO-C(ar)-C(ar)-C(=O)-OH   ->   ring[O-C(ar)-C(ar)-C=O]  +  H2O
#
# This is what makes m/z 120 the base peak of salicylic acid (138 - 18), and it is NOT
# reachable by dehydration_carboxyl above: that rule needs a hydrogen on the carbon
# adjacent to the C-OH, but in salicylic acid that neighbouring ring carbon carries the
# hydroxyl, not a hydrogen. The donor here is an O-H.
#
# Two variants because MOD matches the exact bond order and the pipeline feeds Kekule
# (not aromatic) structures: the ring bond joining the two substituted carbons may come
# out single or double depending on which Kekule form RDKit picked, and matching only
# one makes the rule silently resonance-dependent (the same kekulisation bias already
# known for the term-mode rules). Supplying both keeps it position-invariant.
dehydration_ortho_single = mod.Rule.fromDFS(
    s=
    "[H]1[O]2[C]3[C]4[C]5({=}[O]6)[O]7[H]8"
    ">>"
    "[O]2[C]3[C]4[C]5({=}[O]6){-}2"
    "."
    "[O]7([H]8)([H]1)",
    name=
    "intramolecular water elimination (ortho, O-H donor)"
)

dehydration_ortho_double = mod.Rule.fromDFS(
    s=
    "[H]1[O]2[C]3{=}[C]4[C]5({=}[O]6)[O]7[H]8"
    ">>"
    "[O]2[C]3{=}[C]4[C]5({=}[O]6){-}2"
    "."
    "[O]7([H]8)([H]1)",
    name=
    "intramolecular water elimination (ortho, O-H donor, ene)"
)


# The one that actually matters for a benzoic acid: in the forward DG the intact ring
# is carried as an AROMATIC system (bonds print as ":", e.g.
# "C1:C:C:C(:C(:C:1)O)C(O)=O"), not as a Kekule alternation. A rule written with a
# single or double C3-C4 bond therefore cannot match the molecular ion at all -- which
# is exactly why the two variants above fired only on already-broken, non-aromatic
# intermediates and never produced m/z 120. Matching the aromatic bond keeps the arene
# intact and fuses the lactone onto it.
dehydration_ortho_aromatic = mod.Rule.fromDFS(
    s=
    "[H]1[O]2[C]3:[C]4[C]5({=}[O]6)[O]7[H]8"
    ">>"
    "[O]2[C]3:[C]4[C]5({=}[O]6){-}2"
    "."
    "[O]7([H]8)([H]1)",
    name=
    "intramolecular water elimination (ortho, O-H donor, aromatic)"
)


dehydration_all = [
    dehydration_carboxyl,
    dehydration_ortho_single,
    dehydration_ortho_double,
    dehydration_ortho_aromatic,
]

__all__ = [
    "dehydration_carboxyl",
    "dehydration_ortho_single",
    "dehydration_ortho_double",
    "dehydration_ortho_aromatic",
    "dehydration_all",
]
