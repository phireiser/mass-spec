# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung
# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung

include("../commons.py")

# first branch

benzylAllyl_mz92_91 = Rule.fromDFS(
	"[_A]1[H]2[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4" +
	">>" +
	"[_A]1[H.]2" + "." + "[C+]3[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4"
)

# add term constraint to rule
benzylAllyl_mz92_91 = addConstraints(benzylAllyl_mz92_91, 
# constraint for term variables
"""
constrainLabelAny [
label "_A"
labels [ label "H" label "C" ]
]"""
)

benzylAllyl_mz91_91 = Rule.fromDFS( #full ring
	"[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2" +
	">>" +
	"[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}1"
)

benzylAllyl_mz91_65 = Rule.fromDFS(
	"[C]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1" +
	">>" +
	"[C]1{#}[C]2" + "." + "[C+]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1"
)

benzylAllyl_mz65_39 = Rule.fromDFS( 
	# assumption: is https://en.wikipedia.org/wiki/Cyclopropenium_ion
	# alternative would be https://en.wikipedia.org/wiki/Propargyl_group
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}1" +
	">>" +
	"[C]1{#}[C]2" + "." + "[c+]3{-}[c]4{-}[c]5{-}3"
)

# second branch

benzylAllyl_mz92_77 = Rule.fromDFS( 
	"[_A]1[H]2[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4" +
	">>" +
	"[_A]1[H]2[C.]3" + "." + "[C+]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4"
)

# add term constraint to rule
benzylAllyl_mz92_77 = addConstraints(benzylAllyl_mz92_77, 
# constraint for term variables
"""
constrainLabelAny [
label "_A"
labels [ label "H" label "C" ]
]"""
)

benzylAllyl_mz77_51 = Rule.fromDFS( 
	"[C+]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1" +
	">>" +
	"[C]1{=}[C]2[C]3{=}[C]4{-}" + "." + "[C]5{#}[C]6"
)


benzylAllyl_all = [
    benzylAllyl_mz92_91,
    benzylAllyl_mz91_91,
    benzylAllyl_mz91_65,
    benzylAllyl_mz65_39,
    benzylAllyl_mz92_77,
    benzylAllyl_mz77_51,
]

benzylAllyl_oxidation = [
	benzylAllyl_mz92_91,
	benzylAllyl_mz92_77,
]

benzylAllyl_fragmentation = [
	benzylAllyl_mz91_91,
    benzylAllyl_mz91_65,
    benzylAllyl_mz65_39,
	benzylAllyl_mz77_51,
]