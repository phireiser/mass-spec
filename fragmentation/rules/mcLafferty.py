# https://de.wikipedia.org/wiki/McLafferty-Umlagerung
# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#McLafferty-Umlagerung
# https://doi.org/10.1021/ac60145a015

oxidRule = Rule.fromDFS( 
	# only english wiki
	"[O]1" +
	">>" +
	"[O+.]1",
	name="oxidation Rule")

HrebindRule = Rule.fromDFS( 
	# Educt: only english wiki
	# Product: only german wiki
	"[O+.]1{=}[C]2[C]3[C]4[C]5[H]6" +
	">>" +
	"[O+]1([H]6){=}[C]2[C]3[C]4[C.]5",
	name= "H rebind Rule" )

rearrRule1 = Rule.fromDFS(
	# in german and english wiki
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O+]1{=}[C]2[C.]3.[C]4{=}[C]5",
	name = "rearrangement Rule 1")

rearrRule2 = Rule.fromDFS(
	# in german and english wiki
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O+.]1{-}[C]2{=}[C]3.[C]4{=}[C]5", 
	name = "rearrangement Rule 2")

rearrRule3 = Rule.fromDFS(
	# only in english wiki
	"[O+]1{=}[C]2[C]3[C]4[C.]5" +
	">>" +
	"[O]1[C+]2[C.]3.[C]4{=}[C]5", 
	name = "rearrangment Rule 3")

McLafferty_all = [
	oxidRule,
	HrebindRule,
	rearrRule1,
	rearrRule2,
	rearrRule3,
]