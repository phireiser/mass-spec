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

hTransition_saturated_1 = convert2MoelRule(hTransition_saturated_1)

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

hTransition_saturated_1_alpha = convert2MoelRule(hTransition_saturated_1_alpha)

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

hTransition_saturated_1_inductive_1 = convert2MoelRule(hTransition_saturated_1_inductive_1)

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

hTransition_saturated_1_inductive_2 = convert2MoelRule(hTransition_saturated_1_inductive_2)

hTransition_saturated_1_inductive_2 = labelConstraints_gml(
	input_rules = hTransition_saturated_1_inductive_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_2 = ( # siehe 8.53
	"[H]1[C]2([_Y_1+]6)[_X_1]3[C]4[C.]5" +
	">>" +
	"[_Y_1+]6[C.]2[_X_1]3[C]4([H]1)[C]5",
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

hTransition_saturated_2 = convert2MoelRule(hTransition_saturated_2)

hTransition_saturated_2 = labelConstraints_gml(
	input_rules = hTransition_saturated_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


hTransition_saturated_2_alpha = ( # siehe 8.53
	"[_Y_1+]6[C.]2[_X_1]3[C]4([H]1)[C]5" +
	">>" +
	"[_Y_1+.]6.[C]2([H]1)[_X_1]3[C]4[C]5{-}2",
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

hTransition_saturated_2_alpha = convert2MoelRule(hTransition_saturated_2_alpha)

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

hTransition_saturated_3 = convert2MoelRule(hTransition_saturated_3)

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

hTransition_saturated_3_alpha = convert2MoelRule(hTransition_saturated_3_alpha)

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

hTransition_saturated_4 = convert2MoelRule(hTransition_saturated_4)

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

hTransition_saturated_4_alpha = convert2MoelRule(hTransition_saturated_4_alpha)

hTransition_saturated_4_alpha = labelConstraints_gml(
	input_rules = hTransition_saturated_4_alpha,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


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

hTransition_saturated_5 = convert2MoelRule(hTransition_saturated_5)

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

hTransition_saturated_5_inductive_1 = convert2MoelRule(hTransition_saturated_5_inductive_1)

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

hTransition_saturated_5_inductive_2 = convert2MoelRule(hTransition_saturated_5_inductive_2)

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

hTransition_saturated_5_inductive_3 = convert2MoelRule(hTransition_saturated_5_inductive_3)

hTransition_saturated_5_inductive_3 = labelConstraints_gml(
	input_rules = hTransition_saturated_5_inductive_3,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)