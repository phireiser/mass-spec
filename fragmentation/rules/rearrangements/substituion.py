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

substituion = convert2MoelRule(substituion)

substituion = labelConstraints_gml(
	input_rules = substituion,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)