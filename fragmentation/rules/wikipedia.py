# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Alpha-Spaltung
alpha = Rule.fromDFS(
	"[C]1[C]2({=}[O+.])[C]3[C]4" +
	">>" +
	"[C]1[C]2{#}[O+].[C.]3[C]4", 
	name = "alpha"
)

###############################################################################

# https://en.wikipedia.org/wiki/Fragmentation_(mass_spectrometry)#Charge_site-initiated_cleavage
inductive_wiki = Rule.fromDFS(
	s = 
	"[C]1[C]2[O+.]3[C]4[C]5" +
	">>" +
	"[C]1[C]2[O.]3.[C]4[C+]5", 
	name = 
	"inductive cleavage f. wiki" +
	""
)

###############################################################################

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

###############################################################################

# https://de.wikipedia.org/wiki/McLafferty-Umlagerung
# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#McLafferty-Umlagerung
# https://doi.org/10.1021/ac60145a015

# McLafferty rearrangement is also known as 
# γ-hydrogen rearrangement
# sigma hydrogen rearrangment

# also see MacLafferty book Seite 74 Gleichung 4.33 und 4.34

ml_ionization = Rule.fromDFS( 
	# only english wiki
	s = 
	"[*]1" +
	">>" +
	"[*+.]1",
	name=
	"McL ionization " +
	" §Y1"
)

ml_hRebind = Rule.fromDFS( 
	# Educt: only english wiki
	# Product: only german wiki
	s = 
	"[O+.]1{=}[C]2[C]3[C]4[C]5[H]6" +
	">>" +
	"[O+]1([H]6){=}[C]2[C]3[C]4[C.]5",
	name= 
	"H rebind Rule" +
	""
)

ml_rearrRule1 = Rule.fromDFS(
	# in german and english wiki
	s = 
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O+]1{=}[C]2[C.]3.[C]4{=}[C]5",
	name = 
	"rearrangement Rule 1" +
	""
)

ml_rearrRule2 = Rule.fromDFS(
	# in german and english wiki
	s = 
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O+.]1{-}[C]2{=}[C]3.[C]4{=}[C]5", 
	name = "rearrangement Rule 2")

ml_rearrRule3 = Rule.fromDFS(
	# only in english wiki
	s = 
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O]1[C+]2[C.]3.[C]4{=}[C]5", 
	name = 
	"rearrangment Rule 3" +
	""
)


wiki_ionization = [
    dielsAdler_1,
    ml_ionization,
]

wiki_fragmentation = [
	alpha,
    inductive_wiki,
   	dielsAdler_2a,
	dielsAdler_2b,
    ml_hRebind,
	ml_rearrRule1,
	ml_rearrRule2,
	ml_rearrRule3,
]
