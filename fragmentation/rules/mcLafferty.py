# https://de.wikipedia.org/wiki/McLafferty-Umlagerung
# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#McLafferty-Umlagerung
# https://doi.org/10.1021/ac60145a015

ml_ionization = Rule.fromDFS( 
	# only english wiki
	"[O]1" +
	">>" +
	"[O+.]1",
	name="McL ionization O")

ml_ionization = labelConstraints(ml_ionization, 
	{"O": 
		['B','C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I']
	}
)

ml_hRebind = Rule.fromDFS( 
	# Educt: only english wiki
	# Product: only german wiki
	"[O+.]1{=}[C]2[C]3[C]4[C]5[H]6" +
	">>" +
	"[O+]1([H]6){=}[C]2[C]3[C]4[C.]5",
	name= "H rebind Rule" )

ml_rearrRule1 = Rule.fromDFS(
	# in german and english wiki
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O+]1{=}[C]2[C.]3.[C]4{=}[C]5",
	name = "rearrangement Rule 1")

ml_rearrRule2 = Rule.fromDFS(
	# in german and english wiki
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O+.]1{-}[C]2{=}[C]3.[C]4{=}[C]5", 
	name = "rearrangement Rule 2")

ml_rearrRule3 = Rule.fromDFS(
	# only in english wiki
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O]1[C+]2[C.]3.[C]4{=}[C]5", 
	name = "rearrangment Rule 3")

mcLafferty_all = [
	ml_ionization,
	ml_hRebind,
	ml_rearrRule1,
	ml_rearrRule2,
	ml_rearrRule3,
]
mcLafferty_all = flatten_list(mcLafferty_all)

mcLafferty_ionization = [
	ml_ionization,
]
mcLafferty_ionization = flatten_list(mcLafferty_ionization)

mcLafferty_fragmenation = [
	ml_hRebind,
	ml_rearrRule1,
	ml_rearrRule2,
	ml_rearrRule3,
]
mcLafferty_fragmenation = flatten_list(mcLafferty_fragmenation)