# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Retro-Diels-Alder-Reaktion
# https://de.wikipedia.org/wiki/Diels-Alder-Reaktion#Retro-Diels-Alder-Reaktion
# https://en.wikipedia.org/wiki/Retro-Diels%E2%80%93Alder_reaction

dielsAdler_1 = Rule.fromDFS(
	"[C]1[C+]2[C.]3[C]4[C]5[C]6{-}1" +
	">>" +
	"[C.]5[C]6[C]1[C+]2[C]3{=}[C]4"
)

dielsAdler_2a = Rule.fromDFS( # Homolyse
	"[C.]1[C]2[C]3[C+]4[C]5{=}[C]6" +
	">>" +
	"[C]1{=}[C]2.[C.]3[C+]4[C]5{=}[C]6"
)

dielsAdler_2b = Rule.fromDFS( # Hetrolyse
	"[C.]1[C]2[C]3[C+]4[C]5{=}[C]6" +
	">>" +
	"[C.]1[C+]2.[C]3{=}[C]4[C]5{=}[C]6"
)

dielsAdler_all = [
	dielsAdler_1,
	dielsAdler_2a,
	dielsAdler_2b,
]