# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung
# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung

include("../commons.py")

# first branch

benzylAllyl_mz92_91 = Rule.fromDFS(
	"[_A]1[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4" +
	">>" +
	"[_A+]1" + "." + "[C+]3[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4", # _A. or _A+ makes _H4 for H & C ...
	name = "BA 92-91"
)

benzylAllyl_mz92_91 = labelConstraints(benzylAllyl_mz92_91, 
	{"_A": 
		["H","C"]
	}
)

benzylAllyl_mz91_91 = Rule.fromDFS( # full ring
	"[H]1[C+]3([H]2)[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4" +
	">>" +
	"[H]1[C+]3[C]4([H]2){=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}3",
	name = "BA 91-91 full ring"
)

benzylAllyl_mz91_65 = Rule.fromDFS(
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1" +
	">>" +
	"[C]1{#}[C]2" + "." + "[C+]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}3",
	name = "BA 91-65"
)

benzylAllyl_mz65_39 = Rule.fromDFS( 
	# assumption: is https://en.wikipedia.org/wiki/Cyclopropenium_ion
	# alternative would be https://en.wikipedia.org/wiki/Propargyl_group
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}1" +
	">>" +
	"[C]1{#}[C]2" + "." + "[C+]3{-}[C]4{=}[C]5{-}3",
	name = "BA 65-39"
)

# second branch

benzylAllyl_mz92_77 = Rule.fromDFS( 
	"[_A]1[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4" +
	">>" +
	"[_A]1[C.]3" + "." + "[C+]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4",
	name = "BA 92-77"
)

# add term constraint to rule
benzylAllyl_mz92_77 = labelConstraints(benzylAllyl_mz92_77, 
	{"_A": 
		["H","C"]
	}
)

benzylAllyl_mz77_51 = Rule.fromDFS( 
	"[C+]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1" +
	">>" +
	"[C+]1{=}[C]2[C]3{=}[C]4{-}1" + "." + "[C]5{#}[C]6",
	name = "BA 77-51"
)


benzylAllyl_all = [
    benzylAllyl_mz92_91,
    benzylAllyl_mz91_91,
    benzylAllyl_mz91_65,
    benzylAllyl_mz65_39,
    benzylAllyl_mz92_77,
    benzylAllyl_mz77_51,
]
benzylAllyl_all = flatten_list(benzylAllyl_all)

benzylAllyl_ionizaton = [
	benzylAllyl_mz92_91,
	benzylAllyl_mz92_77,
]
benzylAllyl_ionizaton = flatten_list(benzylAllyl_ionizaton)

benzylAllyl_fragmentation = [
	benzylAllyl_mz91_91,
    benzylAllyl_mz91_65,
    benzylAllyl_mz65_39,
	benzylAllyl_mz77_51,
]
benzylAllyl_fragmentation = flatten_list(benzylAllyl_fragmentation)