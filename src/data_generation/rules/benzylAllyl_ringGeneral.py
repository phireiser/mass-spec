import mod

# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung
#
# Aromaticity-aware form: the benzene / tropylium / cyclopentadienyl+ / phenyl+
# rings are matched and produced as AROMATIC bonds (":" -> term e(ar)), not as one
# arbitrary Kekule alternation. This makes the cascade invariant to which Kekule
# form RDKit would have picked, and lets the ring be matched by these curated rules
# only (generic integer-bond-order rules cannot touch an e(ar) ring). Reaction
# bonds stay explicit: the ejected acetylene is a triple bond (#), and the
# anti-aromatic cyclobutadiene-type 4-ring product (mz77_51) stays Kekule since it
# is not aromatic. Ring topology, charge/radical and H-migration are unchanged from
# the original Kekule rules -- only the ring bond ORDER is generalised to aromatic.


# first branch

benzylAllyl_mz92_91 = mod.Rule.fromDFS(
	s =
	"[_A]1[C]2[C]3:[C]4:[C]5:[C]6:[C]7:[C]8:3"
	">>"
	"[_A+]1" "." "[C+]2[C]3:[C]4:[C]5:[C]6:[C]7:[C]8:3",
	name =
	"BA 92-91"
	" §R1"
)

benzylAllyl_mz91_91 = mod.Rule.fromDFS( # benzyl -> tropylium ring expansion
	s =
	"[H]1[C+]2([H]3)[C]4:[C]5:[C]6:[C]7:[C]8:[C]9:4"
	">>"
	"[H]1[C+]2:[C]4([H]3):[C]5:[C]6:[C]7:[C]8:[C]9:2",
	name =
	"BA 91-91 full ring"
	""
)

benzylAllyl_mz91_65 = mod.Rule.fromDFS( # tropylium -> cyclopentadienyl+ + C2H2
	s =
	"[C+]1:[C]2:[C]3:[C]4:[C]5:[C]6:[C]7:1"
	">>"
	"[C]1{#}[C]2" "." "[C+]3:[C]4:[C]5:[C]6:[C]7:3",
	name =
	"BA 91-65"
	""
)

benzylAllyl_mz65_39 = mod.Rule.fromDFS( # cyclopentadienyl+ -> cyclopropenyl+ + C2H2
	# assumption: is https://en.wikipedia.org/wiki/Cyclopropenium_ion
	# alternative would be https://en.wikipedia.org/wiki/Propargyl_group
	s =
	"[C+]1:[C]2:[C]3:[C]4:[C]5:1"
	">>"
	"[C]1{#}[C]2" "." "[C+]3:[C]4:[C]5:3",
	name =
	"BA 65-39"
	""
)

# second branch

benzylAllyl_mz92_77 = mod.Rule.fromDFS(
	s =
	"[_A]1[C]3[C]4:[C]5:[C]6:[C]7:[C]8:[C]9:4"
	">>"
	"[_A]1[C.]3" "." "[C+]4:[C]5:[C]6:[C]7:[C]8:[C]9:4",
	name =
	"BA 92-77"
	" §R1"
)

benzylAllyl_mz77_51 = mod.Rule.fromDFS(  # phenyl+ -> C4H3+ (anti-aromatic, Kekule) + C2H2
	s =
	"[C+]1:[C]2:[C]3:[C]4:[C]5:[C]6:1"
	">>"
	"[C+]1{=}[C]2[C]3{=}[C]4{-}1" "." "[C]5{#}[C]6",
	name =
	"BA 77-51"
	""
)


benzylAllyl_ionizaton = [
	benzylAllyl_mz92_91,
	benzylAllyl_mz92_77,
]

benzylAllyl_fragmentation = [
	benzylAllyl_mz91_91,
    benzylAllyl_mz91_65,
    benzylAllyl_mz65_39,
	benzylAllyl_mz77_51,
]
