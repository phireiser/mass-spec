import mod

# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung
# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung


# first branch

benzylAllyl_mz92_91 = mod.Rule.fromDFS(
	s = 
	"[_A]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3"
	">>"
	"[_A+]1" "." "[C+]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3",
	name = 
	"BA 92-91"
	" §R1"
)

benzylAllyl_mz91_91 = mod.Rule.fromDFS( # full ring
	s = 
	"[H]1[C+]2([H]3)[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4"
	">>"
	"[H]1[C+]2[C]4([H]3){=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}2",
	name = 
	"BA 91-91 full ring"
	""
)

benzylAllyl_mz91_65 = mod.Rule.fromDFS(
	s = 
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1"
	">>"
	"[C]1{#}[C]2" "." "[C+]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}3",
	name = 
	"BA 91-65"
	""
)

benzylAllyl_mz65_39 = mod.Rule.fromDFS( 
	# assumption: is https://en.wikipedia.org/wiki/Cyclopropenium_ion
	# alternative would be https://en.wikipedia.org/wiki/Propargyl_group
	s = 
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}1"
	">>"
	"[C]1{#}[C]2" "." "[C+]3{-}[C]4{=}[C]5{-}3",
	name = 
	"BA 65-39"
	""
)

# second branch

benzylAllyl_mz92_77 = mod.Rule.fromDFS( 
	s = 
	"[_A]1[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4"
	">>"
	"[_A]1[C.]3" "." "[C+]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4",
	name = 
	"BA 92-77"
	" §R1"
)

benzylAllyl_mz77_51 = mod.Rule.fromDFS( 
	s = 
	"[C+]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1"
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
