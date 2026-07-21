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

hTransition_saturated_2_alpha = mod.Rule.fromDFS( # siehe 8.53
	s =
	# RE-AUTHORED from Gl. 8.53 (book p. 179, "Decompositions of cyclic structures"),
	# which the endpaper's "(*) auch Y" footnote points at. The old form was two
	# "."-separated components AND unreadable as chemistry: the receptor A1 detached
	# from C2 and re-attached to a bare carbon C5 with no stated context, while a
	# hydrogen simultaneously shifted C3 -> C2. Three changes at once, none of them
	# what the book draws.
	#
	# What Gl. 8.53 actually shows for an OE(+.) precursor is plain radical-site
	# alpha-cleavage: the unpaired electron on a carbon pairs with one electron of a
	# bond on the NEIGHBOURING atom, forming a pi bond and expelling whatever that bond
	# held. Here the neighbour C2 carries the onium A3, so the C2-A3 bond breaks
	# homolytically, C1=C2 forms, and A3 leaves as the CHARGED radical.
	#
	# That is the endpaper's "alpha oder rd -- Ladungserhalt, das Ion erhaelt das
	# H-Atom" branch, and it is the exact analogue of hTransition_saturated_1_alpha:
	# same electron bookkeeping, but because A3 sits on the carbon ADJACENT to the
	# radical there is no chain left to close, so the neutral product is an alkene
	# rather than a carbocycle.
	#
	# Matched to the rH product of hTransition_saturated_2 (radical on C1, onium A3 on
	# the neighbouring C2). Conserving by construction: charge 1 -> 1, unpaired 1 -> 1
	# (it moves C1 -> A3), and the two valences freed on C1 (radical) and C2 (lost A3)
	# are exactly the two the new pi bond consumes.
	"[C.]1[C]2([_A+]3)[C]4[C]5"
	">>"
	"[C]1{=}[C]2[C]4[C]5" "." "[_A+.]3",
	name =
	"H transition receptor site saturated alpha"
	" §Y3"
)

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

hTransition_saturated_4 = mod.Rule.fromDFS( # siehe 8.90
	s =
	# RE-AUTHORED from Gl. 8.90 (book p. 204, "Steric effects in OE+. rearrangements"),
	# which the endpaper's third receptor variant ("CH={Y}R", siehe 8.90) points at.
	# Two defects fixed. The left side was two "."-separated components, and -- the
	# reason it could not simply be reconnected -- the old rule delivered the migrating
	# hydrogen to the CARBON C4, which already carried H5 and a double bond to the
	# receptor, so bonding it into the donor chain made that carbon PENTAVALENT.
	#
	# Gl. 8.90 settles it: the hydrogen goes to the HETEROATOM, not to the carbon.
	# The book's example is a long-chain alkanal, R-(CH2)n-CH=O(+.), whose remote C-H
	# reaches round to the ionised carbonyl oxygen; the oxygen ends up as =O(+)H and
	# the radical is left behind on the carbon that gave the hydrogen up. (The
	# subsequent cyclisation and ring cleavage that Gl. 8.90 then draws, expelling
	# C2H4, are separate steps and are not encoded here.)
	#
	# This is NOT redundant with hTransition_unsaturated. There the receptor is bonded
	# into the chain by the double bond itself (...C5{=}A6), giving a six-membered
	# transition state -- the classic McLafferty ring. Here the chain ends in a CARBON
	# that is single-bonded to the chain and double-bonded to the receptor, so the ring
	# is one atom larger. That is exactly why the book notes these eliminations "give
	# rise to abundant product ions not in the spectra of lower homologs (below
	# hexanal)": the longer reach needs the longer chain.
	#
	# The endpaper draws the receptor as "{Y}R", i.e. with a substituent. That variant
	# is deliberately not authored: with =C6 and R already on it, the receptor would be
	# tetravalent once the hydrogen arrives, which only N+ and S+ can be. The plain
	# aldehyde/ketone form below is what Gl. 8.90 itself shows.
	#
	# Conserving: charge 1 -> 1, unpaired 1 -> 1 (it moves A8 -> C2), H1 simply changes
	# owner.
	"[H]1[C]2[C]3[C]4[C]5[C]6([H]7){=}[_A+.]8"
	">>"
	"[C.]2[C]3[C]4[C]5[C]6([H]7){=}[_A+]8[H]1",
	name =
	"H transition receptor site saturated rH"
	" §Y8"
)

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

# hTransition_saturated_5 and its _inductive_1/_2/_3 -- REPLACED by the two rules below.
#
# The old family was unsalvageable. All three inductive rules had a disconnected left
# side ("[C]1([_A+]2) . [C]3[C]4[_A..]5([H]6)"), so MOD applied them across two
# INDEPENDENT fragments, and none of them was charge balanced: _1 turned a +1 precursor
# into a +3 product (marking BOTH C4 and A5 as new cations) and _2/_3 then consumed that
# impossible +3 species and emitted +2. Their precursor hTransition_saturated_5 was never
# in the active list either, so nothing generated their input in the first place.
#
# The root cause was a MISREAD OF THE ENDPAPER. Its fourth receptor variant is drawn
# "{Y}R" with TWO DOTS over the Y -- a LONE PAIR, in the ordinary organic sense. The
# transcription read those dots as two UNPAIRED electrons and wrote "[_A..]", a triplet
# heteroatom, which no step of the mechanism can produce or consume. (The "(**) auch {Y}"
# note to its left carries ONE dot, and that one really is the radical.)
#
# Rather than guess an atom mapping from the schematic, both rules below are transcribed
# directly from Gl. 4.45 itself (book p. 82), which the endpaper cites: the McLafferty
# rearrangement of an ESTER.
#
#     R-CH2-CH2-O-CO-R' (+.)  --rH-->  distonic ion  --alpha-->  R-CH=CH2 + R'C(OH)=O (+.)
#
# Both heteroatoms are written as EXPLICIT oxygen rather than generalized to "_A", even
# though the book extends the reaction to thioesters, amides, phosphates and sulfones
# (p. 81). The reason is a hard limitation of this codebase's term encoding, not chemistry:
# ``encode_vertex_label`` maps EVERY non-alphabetic atom symbol to the single term variable
# ``_A``, so "_A", "_B", "_C" are all the same variable and every placeholder in one rule
# must unify to the SAME element. An ester needs O at both positions and C at R', which as
# "[_A]4 ... [_A+.]6 ... [_A]7" cannot be satisfied by any molecule and matched nothing at
# all (verified: 0 derivations generalized, 3 derivations oxygen-explicit, on ionized ethyl
# acetate). Thioester/amide analogues therefore need their own explicit rules -- one
# generalized rule cannot express them.
#
# PREREQUISITE: these rules consume an ion whose charge and radical sit on the CARBONYL
# heteroatom. The only ionization rule in the library is ``ei_molecular_ion``, "[C]1 >>
# [C+.]1", which ionizes CARBON exclusively, so that species is never generated and these
# rules cannot fire in the pipeline as it currently stands. See the note in
# rules/__init__.py.

esterMcLafferty_rH = mod.Rule.fromDFS( # siehe 4.45 (step 1 of 2)
	s =
	# Gl. 4.45, first step. The gamma hydrogen H1 reaches through space to the ionised
	# carbonyl heteroatom A6 and the radical is left behind on the carbon that gave it
	# up. The transition state is the classic six-membered McLafferty ring:
	# H1, C2, C3, A4, C5, A6.
	#
	#   C2 = gamma carbon (donates H1)      O4 = ester oxygen (lone pair, in chain)
	#   C3 = beta carbon                    C5 = carbonyl carbon
	#   O6 = carbonyl oxygen, ionised       C7 = R' on the carbonyl carbon
	#
	# Conserving: charge 1 -> 1, unpaired 1 -> 1 (O6 -> C2), H1 changes owner. O6 goes
	# from a doubly bonded radical cation (2 bonds) to a doubly bonded cation carrying
	# the hydrogen (3 bonds), which is what "=O(+)H" means.
	#
	# No "§..." extension: every atom is an explicit element, so there is nothing for
	# ``sub_group`` to constrain and it short-circuits to accepted. (Adding one here
	# would be the same silent-veto trap that stopped rules/dehydration.py from firing.)
	"[H]1[C]2[C]3[O]4[C]5({=}[O+.]6)[C]7"
	">>"
	"[C.]2[C]3[O]4[C]5({=}[O+]6[H]1)[C]7",
	name =
	"ester McLafferty rH"
)

esterMcLafferty_alpha = mod.Rule.fromDFS( # siehe 4.45 (step 2 of 2)
	s =
	# Gl. 4.45, second step, matched to the rH product above. Radical-site alpha
	# cleavage: the unpaired electron on C1 pairs with one electron of the C2-A3 bond
	# to form C1=C2, and the other electron goes to A3. The alkene leaves NEUTRAL and
	# the ion keeps both heteroatoms -- it is the acid (enol) radical cation
	# R'C(OH)=O(+.), drawn in the book as the distonic ".O-C(=O(+)H)R'".
	#
	# Same electron bookkeeping as hTransition_saturated_2_alpha above; the two valences
	# freed on C1 (radical) and C2 (lost O3) are exactly the two the new pi bond takes.
	# Conserving: charge 1 -> 1, unpaired 1 -> 1 (C1 -> O3).
	"[C.]1[C]2[O]3[C]4({=}[O+]5[H]6)[C]7"
	">>"
	"[C]1{=}[C]2" "." "[O.]3[C]4({=}[O+]5[H]6)[C]7",
	name =
	"ester McLafferty alpha"
)


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
	hTransition_saturated_2_alpha,   # re-authored from Gl. 8.53

	hTransition_saturated_3,
	hTransition_saturated_3_alpha,

	hTransition_saturated_4,         # re-authored from Gl. 8.90
	hTransition_saturated_4_alpha,

	# The old saturated_5 family (rH + three inductive rules) is REPLACED by the two
	# rules below, transcribed straight from Gl. 4.45 -- see the note at their
	# definition for why the originals could not be repaired.
	esterMcLafferty_rH,
	esterMcLafferty_alpha,

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


# Ionization that feeds esterMcLafferty_rH. Without it that rule has no substrate: the
# library's general ionization is ``ei_molecular_ion`` ("[C]1 >> [C+.]1"), which ionizes
# CARBON only, and the one heteroatom ionization that does exist -- ``ml_ionization`` in
# rules/wikipedia.py -- puts its C-C-C chain on the ACYL side of the carbonyl, whereas
# Gl. 4.45 takes the gamma hydrogen from the ALCOHOL side, through the ester oxygen. So an
# ester's carbonyl oxygen was never ionized and Gl. 4.45 could not start (verified on ethyl
# acetate: no O-centred ion anywhere in its DG).
#
# This follows the ``ml_ionization`` idiom exactly -- ionize in context rather than
# globally -- so it fires only on a genuine Gl. 4.45 substrate (gamma H, beta carbon, ester
# oxygen, carbonyl carbon with an R'), and cannot inflate the DG of a molecule that has no
# ester in it.
#
# NOTE this is a narrow patch, not the general fix. In real EI the most weakly held
# electron is a heteroatom n-electron, so O/N/S ionization is the NORM, and the whole
# "reaction initiation at radical or charge sites" machinery of the book's Chapter 4
# assumes it. A general "[_A]1 >> [_A+.]1 §Y1" rule is one line, and on ethyl acetate it
# additionally recovers m/z 43 (the real base peak) and m/z 29 -- but it widens every DG in
# the corpus, so it wants measuring before it ships. See the note in rules/__init__.py.
esterMcLafferty_ionization = mod.Rule.fromDFS( # siehe 4.45 (ionization)
	s =
	"[H]1[C]2[C]3[O]4[C]5({=}[O]6)[C]7"
	">>"
	"[H]1[C]2[C]3[O]4[C]5({=}[O+.]6)[C]7",
	name =
	"ester McLafferty ionization"
)

IMS_cover_ionization = [
    esterMcLafferty_ionization,
]
