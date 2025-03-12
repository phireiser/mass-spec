# https://en.wikipedia.org/wiki/Fragmentation_(mass_spectrometry)#/media/File:TolueneFragmentation.svg

benzylAlly_mz92_91 = Rule.fromDFS(
	"[H]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3" +
	">>" +
	"[H.]1.[C+]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3"
)

benzylAlly_mz91_91 = Rule.fromDFS( #full ring
	"[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2" +
	">>" +
	"[C]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}1"
)

benzylAlly_mz91_65 = Rule.fromDFS(
	"[C]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1" +
	">>" +
	"[C]1{#}[C]2.[C+]3{-}[C]4{=}[C]5{-}[C]6{=}[C]7{-}1"
)

benzylAlly_mz65_39 = Rule.fromDFS( 
	# assumption: is https://en.wikipedia.org/wiki/Cyclopropenium_ion
	# alternative would be https://en.wikipedia.org/wiki/Propargyl_group
	"[C+]1{-}[C]2{=}[C]3{-}[C]4{=}[C]5{-}1" +
	">>" +
	"[C]1{#}[C]2.[c+]3{-}[c]4{-}[c]5{-}3"
)

# second branch

benzylAlly_mz_92_77 = Rule.fromDFS( 
	"[H]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3" +
	">>" +
	"[H]1[C.]2.[C+]3{=}[C]4[C]5{=}[C]6[C]7{=}[C]8{-}3"
)

benzylAlly_mz77_51 = Rule.fromDFS( 
	"[C+]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1" +
	">>" +
	"[C]1{=}[C]2[C]3{=}[C]4{-}1.[C]5{#}[C]6"
)

benzylAlly_all = [
    benzylAlly_mz92_91,
    benzylAlly_mz91_91,
    benzylAlly_mz91_65,
    benzylAlly_mz65_39,
    benzylAlly_mz_92_77,
    benzylAlly_mz77_51,
]