# rearrangements from mcLafferty book cover

elimination = ( # siehe 4.45
	"[_R_]1[C]2[_X_1]3[C]4[_R_2+]5[_Y_1]6" +
	">>" +
	"[C]2[_X_1]3[C]4{-}2.[_R_1]1[_R_2]5[_Y_1+]6",
	"Elimination"
)

elimination = labelConstraints_dfs(
	input_rules = elimination,
	to_replace = ["_X_1"],
	replacements = saturation_stump_dfs
)

elimination = labelConstraints_dfs(
	input_rules = elimination,
	to_replace = ["_R_1"],
	replacements = saturation_stump_dfs
)

elimination = labelConstraints_dfs(
	input_rules = elimination,
	to_replace = ["_R_2"],
	replacements = saturation_stump_dfs
)

elimination = convert2MoelRule(elimination)

elimination = labelConstraints_gml(
	input_rules = elimination,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)