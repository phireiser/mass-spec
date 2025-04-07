include("../commons.py")
# alpha cleavage


# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Alpha-Spaltung
alpha = Rule.fromDFS(
	"[C]1[C]2({=}[O+.])[C]3[C]4" +
	">>" +
	"[C]1[C]2{#}[O+].[C.]3[C]4", 
	name = "alpha")


# Interpreation von Massenspektren Springer, Seite Einband, gesaettigete stelle
alpha_saturated_site_1 = (
	"[_R_1]1[C]2[_R_2]3([_R_3]4)[_Y_1+.]5[_R_4]6" +
	">>" +
	"[_R_1.]1.[C]2[_R_2]3([_R_3]4){=}[_Y_1+.]5[_R_4]6",
	"radical induced (alpha-)clevage for a saturated site")

alpha_saturated_site_1 = labelConstraints_dfs(
	input_rules = alpha_saturated_site_1, 
	rpl_dict = {
		"_R_1": alkyl_stump_dfs,
		"_R_2": alkyl_stump_dfs,
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite Einband, gesaettigete stelle
alpha_saturated_site_2 = (
	"[_Y_1+]1[_R_1]2[C]3[C.]4" +
	">>" +
	"[_Y_1+.]1[_R_1]2.[C]3[C.]4",
	"radical induced (alpha-)clevage for a saturated site")

alpha_saturated_site_2 = labelConstraints_dfs(
	input_rules = alpha_saturated_site_2, 
	rpl_dict = {
		"_R_1": alkyl_stump_dfs,
		"_R_2": alkyl_stump_dfs,
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite Einband, ungesattigtes heteroatom
alpha_unsaturated_hetroatom = (
	"[_R_1]1[C]2[_R_2]3{=}[_Y_1+.]4" +
	">>" +
	"[_R_1.]1.[C]2[_R_2]3{#}[_Y_1+]4",
	"radical induced (alpha-)clevage for a unsaturated heteroatom")

alpha_unsaturated_hetroatom = labelConstraints_dfs(
	input_rules = alpha_unsaturated_hetroatom, 
	rpl_dict = {
		"_R_1": alkyl_stump_dfs,
		"_R_2": alkyl_stump_dfs,
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_1 = (
	"[_R_1]1[C]2[C]3[C+.]4" +
	">>" +
	"[_R_1.]1[C]2{=}[C]3[C+]4",
	"radical induced (alpha-)clevage for a alkene variant 1")

alpha_alkene_1 = labelConstraints_dfs(
	input_rules = alpha_alkene_1, 
	rpl_dict = {
		"_R_1": alkyl_stump_dfs,
		"_R_2": alkyl_stump_dfs,
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_2 = (
	"[_R_1]1[C]2[C+.]3[C]4" +
	">>" +
	"[_R_1.]1[C]2{=}[C]3[C+]4",
	"radical induced (alpha-)clevage for a alkene variant 2")

alpha_alkene_2 = labelConstraints_dfs(
	input_rules = alpha_alkene_2, 
	rpl_dict = {
		"_R_1": alkyl_stump_dfs,
		"_R_2": alkyl_stump_dfs,
		"_Y_1": heteroAtoms,
	}
)


alpha_fragmentation = [
	alpha,
	alpha_saturated_site_1,
	alpha_saturated_site_2,
	alpha_unsaturated_hetroatom,
	alpha_alkene_1,
	alpha_alkene_2,
]