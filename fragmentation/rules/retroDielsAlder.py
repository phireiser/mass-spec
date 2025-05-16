# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Retro-Diels-Alder-Reaktion
# https://de.wikipedia.org/wiki/Diels-Alder-Reaktion#Retro-Diels-Alder-Reaktion
# https://en.wikipedia.org/wiki/Retro-Diels%E2%80%93Alder_reaction

# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Retro-Diels-Alder-Reaktion
dielsAdler_1 = Rule.fromDFS(
	"[C]1[C+]2[C.]3[C]4[C]5[C]6{-}1" +
	">>" +
	"[C.]5[C]6[C]1[C+]2[C]3{=}[C]4",
	name = "Diels Adler 1 ionization"
)

#https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Retro-Diels-Alder-Reaktion
dielsAdler_2a = Rule.fromDFS( # homolysis
	"[C.]1[C]2[C]3[C+]4[C]5{=}[C]6" +
	">>" +
	"[C]1{=}[C]2.[C.]3[C+]4[C]5{=}[C]6",
	name = "Diels Adler 2 homolysis"
)

#https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Retro-Diels-Alder-Reaktion
dielsAdler_2b = Rule.fromDFS( # hetrolysis
	"[C.]1[C]2[C]3[C+]4[C]5{=}[C]6" +
	">>" +
	"[C.]1[C+]2.[C]3{=}[C]4[C]5{=}[C]6",
	name = "Diels Adler 3 hetrolysis"
)

retroDielsAdler_ionization = [
	dielsAdler_1,
]

retroDielsAdler_fragmentation = [
	dielsAdler_2a,
	dielsAdler_2b,
]