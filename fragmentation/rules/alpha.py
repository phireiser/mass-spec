include("../commons.py")
# alpha cleavage


# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Alpha-Spaltung
alpha = Rule.fromDFS(
	"[C]1[C]2({=}[O+.])[C]3[C]4" +
	">>" +
	"[C]1[C]2{#}[O+].[C.]3[C]4", 
	name = "alpha")


# TODO replace _Y_1, _R_1, _R_2
# R Y are subgraphs


# Interpreation von Massenspektren Springer, Seite Einband, gesaettigete stelle
alpha_saturated_site_1 = Rule.fromDFS(
	"[_R_1]1[C]2[_R_2]3([_R_3]4)[_Y_1+.]5[_R_4]6" +
	">>" +
	"[_R_1.]1.[C]2[_R_2]3([_R_3]4){=}[_Y_1+.]5[_R_4]6",
	name = "radical induced (alpha-)clevage for a saturated site")

# Interpreation von Massenspektren Springer, Seite Einband, gesaettigete stelle
alpha_saturated_site_2 = Rule.fromDFS(
	"[_Y_1+]1[_R_1]2[C]3[C.]4" +
	">>" +
	"[_Y_1+.]1[_R_1]2.[C]3[C.]4",
	name = "radical induced (alpha-)clevage for a saturated site")

# Interpreation von Massenspektren Springer, Seite Einband, ungesattigtes heteroatom
alpha_unsaturated_hetroatom = Rule.fromDFS(
	"[_R_1]1[C]2[_R_2]3{=}[_Y_1+.]4" +
	">>" +
	"[_R_1.]1.[C]2[_R_2]3{#}[_Y_1+]4",
	name = "radical induced (alpha-)clevage for a unsaturated heteroatom")

# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_1 = Rule.fromDFS(
	"[_R_1]1[C]2[C]3[C+.]4" +
	">>" +
	"[_R_1.]1[C]2{=}[C]3[C+]4",
	name = "radical induced (alpha-)clevage for a alkene variant 1")

# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_2 = Rule.fromDFS(
	"[_R_1]1[C]2[C+.]3[C]4" +
	">>" +
	"[_R_1.]1[C]2{=}[C]3[C+]4",
	name = "radical induced (alpha-)clevage for a alkene variant 2")



alpha_fragmentation = [alpha]

alpha_all = [alpha]