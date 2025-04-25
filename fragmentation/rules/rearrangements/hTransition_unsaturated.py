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