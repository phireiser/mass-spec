include("../commons.py")
# rearrangements from mcLafferty book cover

hTransition_unsaturated = Rule.fromDFS(
	"[H]1[C]2[C]3[C]4[C]5{=}[_Y_1+.]6" +
	">>" +
	"[C.]2[C]3[C]4[C]5{=}[_Y_1+]6[H]1", 
	name = "H transition receptor site unsaturated"
)

hTransition_unsaturated = labelConstraints_gml(
	input_rules = hTransition_unsaturated,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_unsaturated_alpha = Rule.fromDFS(
	"[C.]2[C]3[C]4[C]5{=}[_Y_1+]6[H]1" +
	">>" +
	"[C]2{=}[C]3.[C.]4[C]5{=}[_Y_1+]6[H]1",
	name = "H transition receptor site unsaturated"
)


hTransition_unsaturated_alpha = labelConstraints_gml(
	input_rules = hTransition_unsaturated_alpha,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_unsaturated_bidirect = Rule.fromDFS(
	"[C.]2[C]3[C]4[C]5{=}[_Y_1+]6[H]1" +
	">>" +
	"[C.]2[C]3[C]4[C+]5[_Y_1]6[H]1", 
	name = "H transition receptor site unsaturated")

hTransition_unsaturated_bidirect = labelConstraints_gml(
	input_rules = hTransition_unsaturated_bidirect,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_unsaturated_inductive = Rule.fromDFS(
	"[C.]2[C]3[C]4[C]5{=}[_Y_1+]6[H]1" +
	">>" +
	"[C.]2[C+]3.[C]4{=}[C]5[_Y_1]6[H]1", 
	name = "H transition receptor site unsaturated")

hTransition_unsaturated_inductive = labelConstraints_gml(
	input_rules = hTransition_unsaturated_inductive,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)



hTransition_saturated_1 = (
	"[H]1[C]2[_X_1]3[C]4[_Y_1+.]5[_R_1]6" +
	">>" +
	"[C.]2[_X_1]3[C]4[_Y_1+]5([H]1)([_R_1]6)",
	"H transition receptor site saturated"
)

hTransition_saturated_1 = labelConstraints_dfs(
	input_rules = hTransition_saturated_1,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1 = labelConstraints_dfs(
	input_rules = hTransition_saturated_1,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1 = labelConstraints_gml(
	input_rules = hTransition_saturated_1,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_1_alpha = (
	"[C.]2[_X_1]3[C]4[_Y_1+]5([H]1)([_R_1]6)" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[_Y_1+.]5([H]1)([_R_1]6)",
	"H transition receptor site saturated"
)

hTransition_saturated_1_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_1_alpha,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_1_alpha,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1_alpha = labelConstraints_gml(
	input_rules = hTransition_saturated_1_alpha,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_1_inductive_1 = (
	"[C.]2[_X_1]3[C]4[_Y_1+]5([H]1)([_R_1]6)" +
	">>" +
	"[C.]2[_X_1]3[C+]4.[_Y_1+.]5([H]1)([_R_1]6)",
	"H transition receptor site saturated"
)

hTransition_saturated_1_inductive_1 = labelConstraints_dfs(
	input_rules = hTransition_saturated_1_inductive_1,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1_inductive_1 = labelConstraints_dfs(
	input_rules = hTransition_saturated_1_inductive_1,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1_inductive_1 = labelConstraints_gml(
	input_rules = hTransition_saturated_1_inductive_1,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_1_inductive_2 = (
	"[C.]2[_X_1]3[C]4[_Y_1+]5([H]1)([_R_1]6)" +
	">>" +
	"[C]2[_X_1]3[C+.]4{-}2.[_Y_1+.]5([H]1)([_R_1]6)",
	"H transition receptor site saturated inductive"
)

hTransition_saturated_1_inductive_2 = labelConstraints_dfs(
	input_rules = hTransition_saturated_1_inductive_2,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1_inductive_2 = labelConstraints_dfs(
	input_rules = hTransition_saturated_1_inductive_2,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_1_inductive_2 = labelConstraints_gml(
	input_rules = hTransition_saturated_1_inductive_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_2 = ( # siehe 8.53
	"[H]1[C]2([_Y_1+])[_X_1]3[C]4[C.]5" +
	">>" +
	"[C.]2[_X_1]3[C]4([H]1)([_Y_1+])([C]5)",
	"H transition receptor site saturated rH"
)

hTransition_saturated_2 = labelConstraints_dfs(
	input_rules = hTransition_saturated_2,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_2 = labelConstraints_dfs(
	input_rules = hTransition_saturated_2,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_2 = labelConstraints_gml(
	input_rules = hTransition_saturated_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_2_alpha = ( # siehe 8.53
	"[C.]2[_X_1]3[C]4[C]5([H]1)([_Y_1+])" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[C]5([H]1)([_Y_1+])",
	"H transition receptor site saturated alpha"
)

hTransition_saturated_2_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_2_alpha,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_2_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_2_alpha,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_2_alpha = labelConstraints_gml(
	input_rules = hTransition_saturated_2_alpha,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)



hTransition_saturated_3 = ( # siehe 4.44 & 4.46
	"[H]1[C]2[_X_1]3[C]4[_Y_1+]5{=}[C]6([H]7)([_R_1]8)" +
	">>" +
	"[C.]2[_X_1]3[C]4[_Y_1+]5([H]1){=}[C]6([H]7)([_R_1]8)",
	"H transition receptor site saturated rH"
)

hTransition_saturated_3 = labelConstraints_dfs(
	input_rules = hTransition_saturated_3,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_3 = labelConstraints_dfs(
	input_rules = hTransition_saturated_3,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_3 = labelConstraints_gml(
	input_rules = hTransition_saturated_3,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_3_alpha = ( # siehe 4.44 & 4.46
	"[C.]2[_X_1]3[C]4[_Y_1+]5([H]1){=}[C]6([H]7)([_R_1]8)" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[_Y_1+.]5([H]1){=}[C]6([H]7)([_R_1]8)",
	"H transition receptor site saturated alpha"
)

hTransition_saturated_3_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_3_alpha,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_3_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_3_alpha,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_3_alpha = labelConstraints_gml(
	input_rules = hTransition_saturated_3_alpha,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)



hTransition_saturated_4 = ( # siehe 8.90
	"[H]1[C]2[_X_1]3[C]4[C]5([H]6){=}[_Y_1+]7[_R_1]8" +
	">>" +
	"[C.]2[_X_1]3[C]4[C]5([H]7)([H]1){=}[_Y_1+]6[_R_1]8",
	"H transition receptor site saturated rH"
)

hTransition_saturated_4 = labelConstraints_dfs(
	input_rules = hTransition_saturated_4,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_4 = labelConstraints_dfs(
	input_rules = hTransition_saturated_4,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_4 = labelConstraints_gml(
	input_rules = hTransition_saturated_4,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_4_alpha = ( # siehe 8.90
	"[C.]2[_X_1]3[C]4[C]5([H]7)([H]1){=}[_Y_1+]6[_R_1]8" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[C]5([H]7)([H]1){=}[_Y_1+.]6[_R_1]8",
	"H transition receptor site saturated alpha"
)

hTransition_saturated_4_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_4_alpha,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_4_alpha = labelConstraints_dfs(
	input_rules = hTransition_saturated_4_alpha,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_4_alpha = labelConstraints_gml(
	input_rules = hTransition_saturated_4_alpha,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


# TODO:

hTransition_saturated_5 = ( # siehe 4.45
	"[H]1[C]2([_Y_1+])[_X_1]3[C]4[_Y_2..]5[_R_1]6" +
	">>" +
	"[C]2([_Y_1+])[_X_1]3[C]4[_Y_2..]5([H]1)[_R_1]6",
	"H transition receptor site saturated rH"
)

hTransition_saturated_5 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5 = labelConstraints_gml(
	input_rules = hTransition_saturated_5,
	rpl_dict = {
		"_Y_1": heteroAtoms,
		"_Y_2": heteroAtoms,
	}
)


hTransition_saturated_5_inductive_1 = ( # siehe 4.45
	"[C]2([_Y_1+])[_X_1]3[C]4[_Y_2..]5([H]1)[_R_1]6" +
	">>" +
	"[C.]2([_Y_1+])[_X_1]3[C+]4[_Y_2+.]5([H]1)[_R_1]6",
	"H transition receptor site saturated inductive"
)

hTransition_saturated_5_inductive_1 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5_inductive_1,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5_inductive_1 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5_inductive_1,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5_inductive_1 = labelConstraints_gml(
	input_rules = hTransition_saturated_5_inductive_1,
	rpl_dict = {
		"_Y_1": heteroAtoms,
		"_Y_2": heteroAtoms,
	}
)



hTransition_saturated_5_inductive_2 = ( # siehe 4.45
	"[C.]2([_Y_1+])[_X_1]3[C+]4[_Y_2+.]5([H]1)[_R_1]6" +
	">>" +
	"[C.]2([_Y_1+])[_X_1]3[C+]4.[_Y_2.]5([H]1)[_R_1]6",
	"H transition receptor site saturated inductive"
)

hTransition_saturated_5_inductive_2 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5_inductive_2,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5_inductive_2 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5_inductive_2,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5_inductive_2 = labelConstraints_gml(
	input_rules = hTransition_saturated_5_inductive_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_5_inductive_3 = ( # siehe 4.45
	"[C.]2([_Y_1+])[_X_1]3[C+]4[_Y_2+.]5([H]1)[_R_1]6" +
	">>" +
	"[C]2([_Y_1+])[_X_1]3[C+.]4{-}2.[_Y_2.]5([H]1)[_R_1]6",
	"H transition receptor site saturated inductive"
)

hTransition_saturated_5_inductive_3 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5_inductive_3,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5_inductive_3 = labelConstraints_dfs(
	input_rules = hTransition_saturated_5_inductive_3,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

hTransition_saturated_5_inductive_3 = labelConstraints_gml(
	input_rules = hTransition_saturated_5_inductive_3,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


# 2 H Wanderung:


h2Transiton_1 = ( # 2 H Wanderung rH
	"[H]1[C]2([H]3)[C]4[_Y_1]5[C]6([C]7){=}[_Y_2+.]8)" +
	">>" +
	"[C.]2([H]3)[C]4[_Y_1]5[C]6([C]7){=}[_Y_2+]8[H]1)",
	"2 H transition rH1"
)

h2Transiton_1 = labelConstraints_gml(
	input_rules = h2Transiton_1,
	rpl_dict = {
		"_Y_1": heteroAtoms,
		"_Y_2": heteroAtoms,
	}
)


h2Transiton_2 = ( # 2 H Wanderung charge
	"[C.]2([H]3)[C]4[_Y_1]5[C]6([C]7){=}[_Y_2+]8[H]1)" +
	">>" +
	"[C.]2([H]3)[C]4[_Y_1+]5{=}[C]6([C]7)[_Y_2]8[H]1)",
	"2 H transition charge"
)

h2Transiton_2 = labelConstraints_gml(
	input_rules = h2Transiton_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
		"_Y_2": heteroAtoms,
	}
)


h2Transiton_3 = ( # 2 H Wanderung split
	"[C.]2([H]3)[C]4[_Y_1]5[C]6([C]7){=}[_Y_2+]8[H]1" +
	">>" +
	"[C]2{=}[C]4.[H]3[_Y_1+]5{=}[C]6([C]7)[_Y_2]8[H]1",
	"2 H transition rH2 split"
)

h2Transiton_3 = labelConstraints_gml(
	input_rules = h2Transiton_3,
	rpl_dict = {
		"_Y_1": heteroAtoms,
		"_Y_2": heteroAtoms,
	}
)

# Substituion 

substituion = ( # siehe 4.45
	"[R]1[C]2[_X_1]3[C]4[_Y_1+.]5[_R_1]6" +
	">>" +
	"[R.]1.[C]2[_X_1]3[C]4[_Y_1+.]5([_R_1]6){-}2",
	"Substituion"
)

substituion = labelConstraints_dfs(
	input_rules = substituion,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

substituion = labelConstraints_dfs(
	input_rules = substituion,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

substituion = labelConstraints_gml(
	input_rules = substituion,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)

# Elimination

substituion = ( # siehe 4.45
	"[_R_]1[C]2[_X_1]3[C]4[_R_2+]5[_Y_1]6" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[_R_1]1[_R_2]5[_Y_1+]6",
	"Elimination"
)

substituion = labelConstraints_dfs(
	input_rules = substituion,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

substituion = labelConstraints_dfs(
	input_rules = substituion,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

substituion = labelConstraints_dfs(
	input_rules = substituion,
	to_replace = ["_R_2"],
	replacements = saturation_stump_dfs
)

substituion = labelConstraints_gml(
	input_rules = substituion,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)