# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung
# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung

# first branch

benzylAlly_mz91_91_charge = Rule.fromDFS(
    # from german wiki
	s =
	"[C+]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2" +
	">>" +
	"[C]1{=}[C]2[c]3[c]4{=}[c]5[c]6{=}[c]7{-}2",
	name = 
	"BA 91-91 charge" +
	""
)

benzylAlly_mz91_91_charge_reverse = Rule.fromDFS(
    # from german wiki
	s =
    "[C]1{=}[C]2[c]3[c]4{=}[c]5[c]6{=}[c]7{-}2" + #somewhere positive +
	">>" +
    "[C+]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2",
	name = 
	"BA 91-91 charge rev" +
	""
)

benzylAlly_mz91_91 = Rule.fromDFS( # to full ring
    # from english wiki
	s =
	"[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2" +
	">>" +
	"[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}1",
	name = 
	"BA 91-91" +
	""
)

benzylAlly_mz91_91_reverse = Rule.fromDFS( # to full ring reverse
    # from english wiki
	s =
    "[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}1" +
	">>" +
	"[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2",
	name = 
	"BA 91-91 rev" +
	""
)

benzylAlly_mz91_65 = Rule.fromDFS(
    # from english wiki
	s =
	"[C]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1" +
	">>" +
	"[C]1{#}[C]2.[C+]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1",
	name = 
	"BA 91-65" +
	""
)

benzylAlly_mz65_39 = Rule.fromDFS(
    # from english wiki
	# assumption: is https://en.wikipedia.org/wiki/Cyclopropenium_ion
	# alternative would be https://en.wikipedia.org/wiki/Propargyl_group
	s =
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}1" +
	">>" +
	"[C]1{#}[C]2.[c+]3{-}[c]4{-}[c]5{-}3",
	name = 
	"BA 65-39" +
	""
)

# second branch

benzylAlly_mz_92_77 = Rule.fromDFS(
    # from english wiki
	s =
	"[H]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3" +
	">>" +
	"[H]1[C.]2.[C+]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3",
	name =
	"BA 92-77" +
	""
)

benzylAlly_mz77_51 = Rule.fromDFS(
    # from english wiki
	s = 
	"[C+]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1" +
	">>" +
	"[C]1{=}[C]2[C]3{=}[C]4{-}1.[C]5{#}[C]6",
	name =
	"BA 77-51" +
	""
)