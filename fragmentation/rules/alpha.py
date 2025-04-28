include("../commons.py")
# alpha cleavage


# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Alpha-Spaltung
alpha = Rule.fromDFS(
	"[C]1[C]2({=}[O+.])[C]3[C]4" +
	">>" +
	"[C]1[C]2{#}[O+].[C.]3[C]4", 
	name = "alpha"
)


# Interpreation von Massenspektren Springer, Seite Einband, gesaettigete stelle
alpha_saturated_site_1 = (
	"[_R_1]1[C]2[_R_2]3([_R_3]4)[_Y_1+.]5[_R_4]6" +
	">>" +
	"[_R_1.]1.[C]2[_R_2]3([_R_3]4){=}[_Y_1+.]5[_R_4]6",
	"radical induced (alpha-)clevage for a saturated site"
)

alpha_saturated_site_1 = labelConstraints_dfs(
	input_rules = alpha_saturated_site_1, 
	to_replace = ["_R_1", "_R_2", "_R_3", "_R_4"],
	replacements = alkyl_stump_dfs
)

alpha_saturated_site_1  = convert2MoelRule(alpha_saturated_site_1)

#print("dfs", alpha_saturated_site_1[0].getGMLString())
alpha_saturated_site_1 = labelConstraints_gml(
	input_rules = alpha_saturated_site_1,
	rpl_dict = {
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
	to_replace = ["_R_1"],
	replacements = alkyl_stump_dfs
)

alpha_saturated_site_2  = convert2MoelRule(alpha_saturated_site_2)

alpha_saturated_site_2 = labelConstraints_gml(
	input_rules = alpha_saturated_site_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)

# Interpreation von Massenspektren Springer, Seite 60, 4.13
alpha_saturated_site_4_13_1 = (
	"[C]1([H]2)([H]3)([H]4)" +
	"[C]5([H]6)([H]7)" +
	"[O+.]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)" +
	">>" +
	"[C.]1([H]2)([H]3)([H]4)" + 
	".[C]5([H]6)([H]7){=}" +
	"[O+]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)"
	"radical induced (alpha-)clevage for a saturated site 4.13_1")

alpha_saturated_site_4_13_1 = convert2MoelRule(alpha_saturated_site_4_13_1)

alpha_saturated_site_4_13_2 = (
	"[C]1([H]2)([H]3)([H]4)" +
	"[C]5([H]6)([H]7)" +
	"[O+.]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)" +
	">>" +
	"[C.]1([H]2)([H]3)([H]4)" + 
	".[C+]5([H]6)([H]7){-}" +
	"[O]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)"
	"radical induced (alpha-)clevage for a saturated site 4.13_2")

alpha_saturated_site_4_13_2 = convert2MoelRule(alpha_saturated_site_4_13_2)


# Interpreation von Massenspektren Springer, Seite 63, 4.17

alpha_saturated_site_4_17_1 = (
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]5[C]6" +
	"[C]1" +
	"([C]7)" +
	"[O+.]8",
	"radical induced (alpha-)clevage for a saturated site 4.17_1")

alpha_saturated_site_4_17_1 = convert2MoelRule(alpha_saturated_site_4_17_1)


alpha_saturated_site_4_17_1 = (
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]5[C]6" +
	"[C]1" +
	"([C]7)" +
	"[O+.]8" +
	".[C]2[C]3[C]4",
	"radical induced (alpha-)clevage for a saturated site 4.17_1")

alpha_saturated_site_4_17_1 = convert2MoelRule(alpha_saturated_site_4_17_1)


alpha_saturated_site_4_17_2 = (
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]2[C]3[C]4" +
	"[C]1" +
	"([C]7)" +
	"[O+.]8" +
	".[C]5[C]6",
	"radical induced (alpha-)clevage for a saturated site 4.17_2")

alpha_saturated_site_4_17_2 = convert2MoelRule(alpha_saturated_site_4_17_2)


alpha_saturated_site_4_17_3 = (
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]2[C]3[C]4" +
	"[C]1" +
	"([C]5[C]6)" +
	"[O+.]8" +
	".",
	"radical induced (alpha-)clevage for a saturated site 4.17_3")

alpha_saturated_site_4_17_3 = convert2MoelRule(alpha_saturated_site_4_17_3)


# Interpreation von Massenspektren Springer, Seite Einband, ungesattigtes heteroatom
alpha_unsaturated_hetroatom = (
	"[_R_1]1[C]2[_R_2]3{=}[_Y_1+.]4" +
	">>" +
	"[_R_1.]1.[C]2[_R_2]3{#}[_Y_1+]4",
	"radical induced (alpha-)clevage for a unsaturated heteroatom"
)

alpha_unsaturated_hetroatom = labelConstraints_dfs(
	input_rules = alpha_unsaturated_hetroatom, 
	to_replace = ["_R_1", "_R_2"],
	replacements = alkyl_stump_dfs
)

alpha_unsaturated_hetroatom = convert2MoelRule(alpha_unsaturated_hetroatom)

alpha_unsaturated_hetroatom = labelConstraints_gml(
	input_rules = alpha_unsaturated_hetroatom,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)

# Interpreation von Massenspektren Springer, Seite 60, 4.14
alpha_unsaturated_hetroatom_4_14 = (
	"[C]1" +
	"([C]2[C]3)" +
	"([C]4[C]5)" +
	"{=}[O+.]"
	">>" +
	"[C.]2[C]3" +
	".[C]4[C]5" +
	"[C]1{#}[O+]"
	"radical induced (alpha-)clevage for a unsaturated heteroatom 4_14"
)
alpha_unsaturated_hetroatom_4_14 = convert2MoelRule(alpha_unsaturated_hetroatom_4_14)

# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_1 = (
	"[_R_1]1[C]2[C]3[C+.]4" +
	">>" +
	"[_R_1.]1.[C]2{=}[C]3[C+]4",
	"radical induced (alpha-)clevage for a alkene charge left"
)

alpha_alkene_1 = labelConstraints_dfs(
	input_rules = alpha_alkene_1, 
	to_replace = ["_R_1"],
	replacements = alkyl_stump_dfs
)

alpha_alkene_1 = convert2MoelRule(alpha_alkene_1)


# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_2 = (
	"[_R_1]1[C]2[C+.]3[C]4" +
	">>" +
	"[_R_1.]1.[C]2{=}[C]3[C+]4",
	"radical induced (alpha-)clevage for a alkene charge right"
)

alpha_alkene_2 = labelConstraints_dfs(
	input_rules = alpha_alkene_2, 
	to_replace = ["_R_1"],
	replacements = alkyl_stump_dfs
)

alpha_alkene_2 = convert2MoelRule(alpha_alkene_2)

# Interpreation von Massenspektren Springer, Seite 62, 4.15
alpha_alkene_4_15_1_1 = (
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	"radical induced (alpha-)clevage for a alkene 4.15 prod 1 left charge"
)

alpha_alkene_4_15_1_1 = convert2MoelRule(alpha_alkene_4_15_1_1)

alpha_alkene_4_15_1_2 = (
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	"radical induced (alpha-)clevage for a alkene 4.15 prod 1 right charge"
)

alpha_alkene_4_15_1_2 = convert2MoelRule(alpha_alkene_4_15_1_2)


alpha_alkene_4_15_2_1 = (
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C]1.[C+]2[C]3{=}[C]4",
	"radical induced (alpha-)clevage for a alkene 4.15 prod 2 left charge"
)

alpha_alkene_4_15_2_1 = convert2MoelRule(alpha_alkene_4_15_2_1)

alpha_alkene_4_15_2_2 = (
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C+]2[C]3{=}[C]4",
	"radical induced (alpha-)clevage for a alkene 4.15 prod 2 right charge"
)

alpha_alkene_4_15_2_2 = convert2MoelRule(alpha_alkene_4_15_2_2)


alpha_alkene_4_15_3_1 = (
	"[C]1[C]2[C+.]3[C]4[C]5[C]6[C]7[C]8" +
	">>" +
	"[C]1.[C]2{=}[C+]3[C]4[C]5[C]6[C]7[C]8",
	"radical induced (alpha-)clevage for a alkene 4.15 2nd prod 1"
)

alpha_alkene_4_15_3_1 = convert2MoelRule(alpha_alkene_4_15_3_1)


alpha_alkene_4_15_3_2 = (
	"[C]1[C]2[C]3[C+.]4[C]5[C]6[C]7[C]8" +
	">>" +
	"[C.]1.[C+]2[C]3[C]4[C]5[C]6[C]7[C]8",
	"radical induced (alpha-)clevage for a alkene 4.15 2nd prod 2"
)

alpha_alkene_4_15_3_2 = convert2MoelRule(alpha_alkene_4_15_3_2)

alpha_fragmentation = [
	alpha,
	alpha_saturated_site_1,
	alpha_saturated_site_2,
	alpha_unsaturated_hetroatom,
	alpha_alkene_1,
	alpha_alkene_2,

	# examples:
	alpha_saturated_site_4_13_1,
	alpha_saturated_site_4_13_2,

	alpha_unsaturated_hetroatom_4_14,

	alpha_alkene_4_15_1_1,
	alpha_alkene_4_15_1_2,
	alpha_alkene_4_15_2_1,
	alpha_alkene_4_15_2_2,
	alpha_alkene_4_15_3_1,
	alpha_alkene_4_15_3_2,

	alpha_saturated_site_4_17_1,
	alpha_saturated_site_4_17_2,
	alpha_saturated_site_4_17_3,
]

alpha_fragmentation = flatten_list(alpha_fragmentation)