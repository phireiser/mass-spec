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
	"H transition receptor site saturated"
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


hTransition_saturated_1_inductive_2 = (
	"[C.]2[_X_1]3[C]4[_Y_1+]5([H]1)([_R_1]6)" +
	">>" +
	"[C]2[_X_1]3[C+.]4{-}2.[_Y_1+.]5([H]1)([_R_1]6)",
	"H transition receptor site saturated"
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
	"[C]2([H]1)([_Y_1+])[_X_1]3[C]4[C.]5" +
	">>" +
	"[C.]2[_X_1]3[C]4([H]1)([_Y_1+])([C]5)",
	"H transition receptor site saturated"
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
	"H transition receptor site saturated"
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
	"[H]1[C]2[_X_1]3[C]4[_Y_1+]{=}[C]5([H]6)([_R_1]7)" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[_Y_1+]{-}[C]5([H]1)",
	"H transition receptor site saturated"
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


hTransition_saturated_3_alpha = ( # siehe 8.44 & 4.46
	"[C.]2[_X_1]3[C]4[C]5([H]1)([_Y_1+])" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[C]5([H]1)([_Y_1+])",
	"H transition receptor site saturated"
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