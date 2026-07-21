import mod


# Interpreation von Massenspektren Springer, Einband Seiten

#IMS_4_7

# element with low IE
sigma_lowIE = mod.Rule.fromDFS(
	s =
	"[_A+.]1[I]2"
	">>"
	"[_A.]1" "." "[I+]2",
	name =
	"dissoziation of a sigma bond for Elements with low IE"
	" §R1"
)

#IMS_4_9 gesattigte Stelle

#IMS_4_10 gesattigte Stelle

#IMS_4_11 ungesaettigtes Heteroatom

#IMS_4_12 Alkene (Allylspaltung)


#IMS_4_31 Retro-Diels-Alder

#IMS_4_32 Retro-Diels-Alder


#IMS_4_18 OE+. hetrolytische Dissioziation

#IMS_4_20 EE+. hetrolytische Dissioziation


####### h Transtion unsaturated

hTransition_unsaturated = mod.Rule.fromDFS(
	s =
	"[H]1[C]2[C]3[C]4[C]5{=}[_A+.]6"
	">>"
	"[C.]2[C]3[C]4[C]5{=}[_A+]6[H]1",
	name =
	"H transition receptor site unsaturated"
	" §Y6"
)

hTransition_unsaturated_alpha = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2[C]3[C]4{=}[_A+]5[H]6"
	">>"
	"[C]1{=}[C]2" "." "[C.]3[C]4{=}[_A+]5[H]6",
	name =
	"H transition receptor site unsaturated"
	" §Y5"
)

hTransition_unsaturated_bidirect = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2[C]3[C]4{=}[_A+]5[H]6"
	">>"
	"[C.]1[C]2[C]3[C+]4[_A]5[H]6",
	name =
	"H transition receptor site unsaturated"
	" §Y5"
)

hTransition_unsaturated_inductive = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2[C]3[C]4{=}[_A+]5[H]6"
	">>"
	"[C.]1[C+]2" "." "[C]3{=}[C]4[_A]5[H]6",
	name =
	"H transition receptor site unsaturated"
	" §Y5"
)

####### hTranstion saturated

hTransition_saturated_1 = mod.Rule.fromDFS(
	s =
	# CONNECTED (was two "."-separated components -- the bimolecular mis-encoding).
	# The book draws ONE molecule: a U-shaped chain carrying the migrating H on the far
	# carbon and the saturated receptor YR at the other end, with the curved arrow
	# showing the H hopping ACROSS SPACE over the loop (a 6-membered TS: H1, C2..C5, A6).
	# Donor and receptor are joined by the carbon chain -- there is no second molecule
	# anywhere in the figure. A top-level "." makes MOD read the rule as k-ary and pair
	# two INDEPENDENT fragments instead. This now mirrors hTransition_unsaturated
	# exactly, differing only in the SINGLE (saturated) C5-A6 bond where that rule
	# has "{=}" -- which is precisely what "gesaettigte Rezeptorstelle" means.
	"[H]1[C]2[C]3[C]4[C]5[_A+.]6"
	">>"
	"[C.]2[C]3[C]4[C]5[_A+]6[H]1",
	name =
	"H transition receptor site saturated"
	" §Y6"
)

hTransition_saturated_1_alpha = mod.Rule.fromDFS(
	s =
	# CONNECTED, and matched to the rH product above (radical on C1, chain C1..C4, the
	# onium A5 on C4). This is the book's "alpha oder rd" branch, Gl. 4.37/4.39:
	# "Ladungserhalt, das Ion erhaelt das H-Atom" -- the radical carbon attacks C4,
	# closing a carbocycle and displacing the receptor, which leaves as the CHARGED
	# HYR(+.) keeping its hydrogen while the ring is neutral. Same outcome as the
	# atom-explicit reference IMS_4_37_rd (which likewise closes a 4-membered ring and
	# expels [O+.]H2).
	"[C.]1[C]2[C]3[C]4[_A+]5([H]6)"
	">>"
	"[C]1[C]2[C]3[C]4{-}1" "." "[_A+.]5([H]6)",
	name =
	"H transition receptor site saturated"
	" §Y5"
)

hTransition_saturated_1_inductive_1 = mod.Rule.fromDFS(
	s =
	# CONNECTED, matched to the rH product (radical C1, chain C1..C4, onium A5 on C4).
	# The book's "i" branch, Gl. 4.38/4.40: "Ladungswanderung, das Ion verliert das
	# H-Atom", drawn with "- HYR" over the arrow. The C4-A5 bond breaks HETEROLYTICALLY
	# -- the onium takes the pair and leaves as a closed-shell NEUTRAL HYR (so the ion
	# loses the hydrogen), the carbon keeps the charge, and the radical stays put. The
	# product is exactly the open distonic radical cation the book draws (a dot at one
	# end, a plus at the other). Same as the atom-explicit IMS_4_38_ind, which writes
	# the departing oxygen as neutral [O]7.
	"[C.]1[C]2[C]3[C]4[_A+]5([H]6)"
	">>"
	"[C.]1[C]2[C]3[C+]4" "." "[_A]5([H]6)",
	name =
	"H transition receptor site saturated"
	" §Y5"
)

# hTransition_saturated_1_inductive_2 -- REMOVED, not merely disabled.
#
# In the book this is not a cleavage of its own: Gl. 4.38/4.40 shows it only as the
# PARENTHESISED follow-up "( ---> ring )", i.e. the open distonic radical cation
# produced by hTransition_saturated_1_inductive_1 subsequently cyclising. It is an
# isomerisation of that ion, not a second way to break the C-Y bond.
#
# It cannot be written as a conserving one-step localised rewrite. Closing the ring
# means joining the radical carbon to the cationic carbon, and that sigma bond needs
# two electrons: the radical supplies one and the carbocation supplies none. Any
# localised product therefore either invents an electron or drops the charge -- which
# is exactly how the original ended up marking BOTH carbons as radical cations
# (charge 1->2, radical 1->2). Balancing the label counts alone does not fix it,
# because the bond count still rises by one with nothing to pay for it.
#
# Its old left side was also two "."-separated components, so MOD applied it
# bimolecularly across two independent fragments -- the mis-encoding this file is
# being cleaned of.
#
# To reinstate it, author it as a genuine ring closure of the INDUCTIVE PRODUCT with
# the accompanying charge/H shift that makes the electron count work out (a cyclic
# radical cation whose charge and spin sit on ring atoms that are not the two being
# bonded), and validate it against Gl. 4.38/4.40 -- do not resurrect the old form.

hTransition_saturated_2 = mod.Rule.fromDFS( # siehe 8.53
	s =
	# CONNECTED, and the charge site no longer migrates. This is the cover's "(*) auch Y"
	# footnote (siehe 8.53): the receptor is a RADICAL CARBON rather than a heteroatom, so
	# the through-space rH moves the hydrogen onto that radical carbon and leaves the
	# radical behind on the donor carbon. Two defects fixed: the left side was two
	# independent fragments, and the charge-bearing A4 sat on C3 in the reactant but on C2
	# in the product -- a spurious 1,2-migration of the charge site that no step of this
	# mechanism performs. A4 now stays on C3, and the H lands on the carbon that actually
	# carried the radical (previously it was placed on its neighbour C5 instead).
	"[H]1[C]2[C]3([_A+]4)[C]5[C.]6"
	">>"
	"[C.]2[C]3([_A+]4)[C]5[C]6([H]1)",
	name =
	"H transition receptor site saturated rH"
	" §Y4"
)

# hTransition_saturated_2_alpha -- DISABLED pending a proper re-authoring.
#
# Its left side was two "."-separated components, so MOD applied it bimolecularly
# across two independent fragments -- the mis-encoding this file is being cleaned of.
# Unlike the saturated_1/2/3 rules it cannot simply be reconnected, because as written
# the receptor A1 DETACHES from C2 and re-attaches to a bare carbon C5 that has no other
# stated context (the reviewer flagged the resulting centre as over-valent), while a
# hydrogen simultaneously shifts C3 -> C2. That is three changes at once and the
# intended topology is not recoverable from the cover figure alone; it is the "(*) auch
# Y" footnote pointing at Gl. 8.53, which is not drawn on the endpaper.
# Re-derive it from Gl. 8.53 as a SINGLE connected component before re-enabling.

hTransition_saturated_3 = mod.Rule.fromDFS( # siehe 4.44 & 4.46
	s =
	# FIX: the receptor must be a RADICAL cation [_A+.], not a closed-shell cation.
	# The book's saturated receptor site is an odd-electron ion, and the rH step is a
	# homolytic H-atom migration that leaves the radical on C2. Written as [_A+] the
	# rule created that unpaired electron out of nothing (radical 0 -> 1), which an
	# even-electron ion cannot do.
	# CONNECTED (was two "."-separated components). Same single-molecule, through-space
	# 6-membered-TS geometry as hTransition_saturated_1; this variant only decorates the
	# receptor with an extra {=}C substituent (Gl. 4.44/4.46). The "S3-4" part of the old
	# extension existed to constrain the unspecified gap between the two components and
	# is no longer needed now that the chain is explicit.
	"[H]1[C]2[C]3[C]4[C]5[_A+.]6{=}[C]7([H]8)([_A]9)"
	">>"
	"[C.]2[C]3[C]4[C]5[_A+]6([H]1){=}[C]7([H]8)([_A]9)",
	name =
	"H transition receptor site saturated rH"
	" §Y6R9"
)

hTransition_saturated_3_alpha = mod.Rule.fromDFS( # siehe 4.44 & 4.46
	s =
	# CONNECTED, matched to the rH product above. Same alpha/rd branch as
	# hTransition_saturated_1_alpha (radical carbon closes the carbocycle, the receptor
	# departs as the charged HYR(+.) keeping its hydrogen), with the extra {=}C
	# decoration carried through.
	"[C.]1[C]2[C]3[C]4[_A+]5([H]6){=}[C]7([H]8)([_A]9)"
	">>"
	"[C]1[C]2[C]3[C]4{-}1" "." "[_A+.]5([H]6){=}[C]7([H]8)([_A]9)",
	name =
	"H transition receptor site saturated alpha"
	" §Y5R9"
)

# hTransition_saturated_4 -- DISABLED pending a proper re-authoring.
#
# Left side was two "."-separated components (bimolecular mis-encoding). Reconnecting it
# is not mechanical: the acceptor carbon already carries a hydrogen and a double bond to
# the receptor, so simply bonding it into the donor chain makes it PENTAVALENT. Making it
# work requires choosing whether the chain attaches to the carbon or to the heteroatom,
# and whether the C={A} pi bond collapses to a single bond as the hydrogen arrives --
# a decision that needs Gl. 8.90, which is not drawn on the endpaper this file encodes.
# Re-derive from Gl. 8.90 as a SINGLE connected component before re-enabling.

hTransition_saturated_4_alpha = mod.Rule.fromDFS( # siehe 8.90
	s =
	# FIX: C4 was PENTAVALENT on both sides -- it carried C3, H5, H6 and a double bond
	# to O7 (3 single + 1 double = 5 bonds). Dropped the second hydrogen so the carbon
	# is tetravalent; the transformation itself (ring closure C1-C3, O7 becoming a
	# radical cation as the C4-O7 fragment departs) is unchanged.
	"[C.]1[C]2[C]3[C]4([H]5){=}[O+]7[C]8"
	">>"
	"[C]1[C]2[C]3{-}1" "." "[C]4([H]5){=}[O+.]7[C]8",
	name =
	"H transition receptor site saturated alpha"
	"" #TODO no rule enhancemend?
)

hTransition_saturated_5 = mod.Rule.fromDFS( # siehe 4.45
	s =
	"[H]1[C]2([_A+]3)[C]4[C]5[_A..]6" #YRY "[H]1[C]2([_A+]3)[C]4[C]5[_A..]6[_A]7"
	">>"
	"[C]2([_A+]3)[C]4[C]5[_A..]6([H]1)", #YRY "[C]2([_A+]3)[C]4[C]5[_A..]6([H]1)[_A]7"
	name =
	"H transition receptor site saturated rH"
	" §Y6S2-4Y3" #YRY " §Y6S2-4Y3R7"
)

# hTransition_saturated_5_inductive_1 / _2 / _3 -- REMOVED (were BIMOLECULAR and unbalanced).
#
# All three had a disconnected left side ("[C]1([_A+]2) . [C]3[C]4[_A..]5([H]6)"), so MOD
# applied them across two INDEPENDENT fragments -- the mis-encoding this file is being
# cleaned of. They were also never chargebalanced: _1 turned a +1 precursor into a +3
# product (marking BOTH C4 and A5 as new cations) and _2/_3 then consumed that impossible
# +3 species and emitted +2.
#
# They cannot be repaired by reconnecting alone, because the whole family hangs off a
# receptor written as "[_A..]" -- TWO unpaired electrons, i.e. a triplet heteroatom. The
# mechanism needs a mono-radical "[_A.]", so the intended reactant is not recoverable from
# the endpaper; Gl. 4.45 (the "(**) auch Y" footnote they cite) is a lactone/ester case
# that is not drawn on the cover.
#
# Their precursor hTransition_saturated_5 (above) is itself not wired into the active list,
# so nothing generated their input in the first place.
#
# Re-derive the whole family from Gl. 4.45 as SINGLE connected components, with a
# mono-radical receptor, before reinstating any of it.


####### h2Transiton

h2Transiton_1 = mod.Rule.fromDFS(# 2 H-migr. rH 4.46
	s=
	"[H]1[C]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+.]8"
	">>"
	"[C.]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+]8[H]1",
	name=
	"2 H transition rH1"
	" §Y5Y8"
)

h2Transiton_2 = mod.Rule.fromDFS(# 2 H-migr. charge 4.46
	s=
	"[C.]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+]8[H]1"
	">>"
	"[C.]2([H]3)[C]4[_A+]5{=}[C]6([C]7)[_A]8[H]1",
	name =
	"2 H transition charge"
	" §Y5Y8"
)

h2Transiton_3 = mod.Rule.fromDFS( # 2 H-migr. split 4.46
	s=
	"[C.]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+]8[H]1"
	">>"
	# FIX: the unpaired electron must survive the split. Forming C2=C4 consumes C2's
	# radical, so writing BOTH products closed-shell lost it (radical 1 -> 0) -- an
	# odd-electron precursor can never give two even-electron fragments. The C4-A5
	# homolysis leaves the odd electron on A5, so the ion is a radical cation.
	"[C]2{=}[C]4"
	"."
	"[H]3[_A+.]5{=}[C]6([C]7)[_A]8[H]1",
	name =
	"2 H transition rH2 split"
	" §Y5Y8"
)

####### substituion

substituion = mod.Rule.fromDFS( # siehe 4.42
	s =
	"[_A]1[C]2[C]3[_A+.]4" #YRY "[_A]1[C]2.[C]3[_A+.]4[_A]5"
	">>"
	"[_A.]1"
	"."
	# FIX: removed a stray "." between C2 and C3. It severed the C2-C3 backbone bond, so
	# the product was an open C2-A4-C3 chain instead of the 3-membered ring the book
	# draws for the rd substitution (Gl. 4.42): A4 attacks C2, displacing R, and the
	# ring closes over the retained C2-C3 bond. Same formula either way, so the mass
	# spectrum was unaffected -- but the connectivity was wrong and fed wrong products
	# to any downstream rule.
	"[C]2[C]3[_A+]4{-}2", #YRY "[_A.]1.[C]2[C]3[_A+]4([_A]5){-}2"
	name=
	"Substituion"
	" §R1S2-3Y4" #YRY " §R1S2-3Y4R5"
)

####### elimination

# TODO: check if elimination is correct, verify with book
#elimination = mod.Rule.fromDFS( # siehe Tab. 8.4
#	s =
#	"[_A]1[C]2" "." "[C]3[_A+]4[_A]5"
#	">>"
#	"[C]2"
#	"."
#	"[C]3{-}2.[_A]1[_A]4[_A+]5",
#	name =
#	"Elimination"
#	" §R1S2-3R4Y5"
#)



rearrangements = [
	hTransition_unsaturated,
	hTransition_unsaturated_alpha,
	hTransition_unsaturated_bidirect,
	hTransition_unsaturated_inductive,

	hTransition_saturated_1,
	hTransition_saturated_1_alpha,
	hTransition_saturated_1_inductive_1,
	# hTransition_saturated_1_inductive_2 removed -- see the note at its definition.

	hTransition_saturated_2,
	# hTransition_saturated_2_alpha disabled -- see note at its definition.

	hTransition_saturated_3,
	hTransition_saturated_3_alpha,

	# hTransition_saturated_4 disabled -- see note at its definition.
	hTransition_saturated_4_alpha,

	# The saturated_5 inductive family was REMOVED entirely -- see the note at its
	# former definition site.
	#  * _inductive_1 turns a +1 precursor into a +3 product (it marks BOTH C4 and A5
	#    as new cations), and _2/_3 then consume that impossible +3 species and emit +2
	#    -- charge is conserved by none of the three.
	#  * They all hang off the receptor written as [_A..] (TWO unpaired electrons). The
	#    mechanism needs a mono-radical [_A.]; a triplet heteroatom is not what the book
	#    draws, so the intended reactant is unclear.
	#  * Their precursor rule hTransition_saturated_5 is itself not in this list, so
	#    nothing generates their input in the first place.
	# Re-derive from the book (Gl. 4.45) before re-enabling.

	h2Transiton_1,
	h2Transiton_2,
	h2Transiton_3,
	substituion,
	# elimination,
]


IMS_cover_fragmentation = [
    sigma_lowIE,
]

IMS_cover_fragmentation.extend(rearrangements)
