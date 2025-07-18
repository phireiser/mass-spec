# https://en.wikipedia.org/wiki/Fragmentation_(mass_spectrometry)#/media/File:TolueneFragmentation.svg

benzylAllyl_mz92_91 = Rule.fromDFS(
	s = 
	"[H]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3"
	">>"
	"[H.]1" "." "[C+]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3",
	name = 
	"BA 92-91"
	""
)

benzylAllyl_mz91_91 = Rule.fromDFS( # full ring
	s =
	"[H]1[C+]3([H]2)[C]4{=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}4"
	">>"
	"[H]1[C+]3[C]4([H]2){=}[C]5[C]6{=}[C]7[C]8{=}[C]9{-}3",
	name = 
	"BA 91-91 full ring"
	""
)

benzylAllyl_mz91_65 = Rule.fromDFS(
	s = 
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1"
	">>"
	"[C]1{#}[C]2" "." "[C+]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}3",
	name = 
	"BA 91-65"
	""
)

benzylAllyl_mz65_39 = Rule.fromDFS( 
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

benzylAllyl_mz92_77 = Rule.fromDFS( 
	s = 
	"[H]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3"
	">>"
	"[H]1[C.]2" "." "[C+]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3",
	name = 
	"BA 92-77"
	""
)

benzylAllyl_mz77_51 = Rule.fromDFS(
	s = 
	"[C+]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1"
	">>"
	"[C+]1{=}[C]2[C]3{=}[C]4{-}1" "." "[C]5{#}[C]6",
	name = 
	"BA 77-51"
	""
)


benzylAllyl_all = [
    benzylAllyl_mz92_91,
    benzylAllyl_mz91_91,
    benzylAllyl_mz91_65,
    benzylAllyl_mz65_39,
    benzylAllyl_mz92_77,
    benzylAllyl_mz77_51,
]

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