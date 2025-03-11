# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung

benzylAlly_mz134_77 = Rule.fromDFS(
	"[C]1[C]2[C]3[C]4[C]5{=}[C]6[C]7{=}[C]8[C]9{=}[C]10{-}5" +  #somewhere positive radical +.
	">>" +
	"[C]1[C]2[C]3.[C]4{=}[C]5[c]6[c]7{=}[c]8[c]9{=}[c]10{-}5"
)

benzylAlly_mz134_91 = Rule.fromDFS(
	"[C]1[C]2[C]3[C]4[C]5{=}[C]6[C]7{=}[C]8[C]9{=}[C]10{-}5" + #somewhere positive radical +.
	">>" +
	"[C]1[C]2[C.]3.[C]4[C]5{=}[C]6[C]7{=}[C]8[C]9{=}[C]10{-}5" #somewhere positive + and H.
)

benzylAlly_mz77_51 = Rule.fromDFS(
	"[C]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1" +  #somewhere positive +
	">>" +
	"[C]1{=}[C]2[C]3{=}[C]4{-}1.[C]5{#}[C]6"  #somewhere positive +
)

benzylAlly_mz91_91_charge = Rule.fromDFS(
	"[C]1{=}[C]2[c]3[c]4{=}[c]5[c]6{=}[c]7{-}2" #somewhere positive +
	">>" +
	"[C+]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2"
)

benzylAlly_mz91_91_ring = Rule.fromDFS(
	"[C]1{=}[C]2[c]3[c]4{=}[c]5[c]6{=}[c]7{-}2" #ring positive +
	">>" +
	"[c]1{=}[c]2{-}[c]3{=}[c]4{-}[c]5{=}[c]6{-}[c]7{-}1" #ring positive +
)

benzylAlly_mz91_65 = Rule.fromDFS(
	"[c]1{=}[c]2{-}[c]3{=}[c]4{-}[c]5{=}[c]6{-}[c]7{-}1" #ring positive +
	">>" +
	"[C]1{#}[C]2.[c]3{=}[c]4{-}[c]5{=}[c]6{-}[c]7{-}1" #ring positive +
)

benzylAlly_all = [
    benzylAlly_mz134_77,
    benzylAlly_mz134_91,
    benzylAlly_mz77_51,
    benzylAlly_mz91_91_charge,
    benzylAlly_mz91_91_ring,
    benzylAlly_mz91_65,
]


#TODO: as no charges done: do charges
#TODO: backedges