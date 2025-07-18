# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Benzyl-Allylspaltung
# https://upload.wikimedia.org/wikipedia/commons/f/f2/Benzylspaltung.svg

benzylAllyl_mz134_77 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C]4[C]5{=}[C]6[C]7{=}[C]8[C]9{=}[C]10{-}5" +  #somewhere positive radical +.
	">>" +
	"[C]1[C]2[C]3" "." "[C]4{=}[C]5[c]6[c]7{=}[c]8[c]9{=}[c]10{-}5",
	name = 
	"BA 134-77" +
	""
)

benzylAllyl_mz134_91 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3[C]4[C]5{=}[C]6[C]7{=}[C]8[C]9{=}[C]10{-}5" + # somewhere positive radical +.
	">>" +
	"[C]1[C]2[C.]3" "." "[C]4[C]5{=}[C]6[C]7{=}[C]8[C]9{=}[C]10{-}5", # somewhere positive + and H.
	name = 
	"BA 134-91" +
	""
)

benzylAllyl_mz77_51 = Rule.fromDFS(
	s = 
	"[C]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6{-}1" +  # somewhere positive +
	">>" +
	"[C]1{=}[C]2[C]3{=}[C]4{-}1" "." "[C]5{#}[C]6",  # somewhere positive +
	name = 
	"BA 77-51" +
	""
)

benzylAllyl_mz91_91_charge = Rule.fromDFS(
	s = 
	"[C]1{=}[C]2[c]3[c]4{=}[c]5[c]6{=}[c]7{-}2" + # somewhere positive +
	">>" +
	"[C+]1[C]2{=}[C]3[C]4{=}[C]5[C]6{=}[C]7{-}2",
	name = 
	"BA 91-91 charge bond variant" +
	""
)

benzylAllyl_mz91_91_ring = Rule.fromDFS(
	s = 
	"[C]1{=}[C]2[c]3[c]4{=}[c]5[c]6{=}[c]7{-}2" + #ring positive +
	">>" +
	"[c]1{=}[c]2{-}[c]3{=}[c]4{-}[c]5{=}[c]6{-}[c]7{-}1", #ring positive +
	name = 
	"BA 91-91 full ring" +
	""
)

benzylAllyl_mz91_65 = Rule.fromDFS(
	# for transparency: https://www.researchgate.net/figure/Cyclopentenium-cation-cyclo-C5H7-or-CP-cyclopentadienyl-cation-cyclo-C5H5-the_fig1_374533853
	s = 
	"[c]1{=}[c]2{-}[c]3{=}[c]4{-}[c]5{=}[c]6{-}[c]7{-}1" + #ring positive +
	">>" +
	"[C]1{#}[C]2" "." "[c]3{=}[c]4{-}[c]5{=}[c]6{-}[c]7{-}1", #ring positive +
	name = 
	"BA 91-65" +
	""
)


benzylAllyl_all = [
    benzylAllyl_mz134_77,
    benzylAllyl_mz134_91,
    benzylAllyl_mz77_51,
    benzylAllyl_mz91_91_charge,
    benzylAllyl_mz91_91_ring,
    benzylAllyl_mz91_65,
]

benzylAllyl_ionizaton = [

]

benzylAllyl_fragmentation = [
	benzylAllyl_mz134_77,
    benzylAllyl_mz134_91,
    benzylAllyl_mz77_51,
    benzylAllyl_mz91_91_charge,
    benzylAllyl_mz91_91_ring,
    benzylAllyl_mz91_65,
]


#TODO: as no charges done: do charges