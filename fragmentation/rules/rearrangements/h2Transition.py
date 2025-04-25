h2Transiton_1 = ( # 2 H Wanderung rH
	"[H]1[C]2([H]3)[C]4[_Y_1]5[C]6([C]7){=}[_Y_2+.]8" +
	">>" +
	"[C.]2([H]3)[C]4[_Y_1]5[C]6([C]7){=}[_Y_2+]8[H]1",
	"2 H transition rH1"
)

h2Transiton_1 = convert2MoelRule(h2Transiton_1)

h2Transiton_1 = labelConstraints_gml(
	input_rules = h2Transiton_1,
	rpl_dict = {
		"_Y_1": heteroAtoms,
		"_Y_2": heteroAtoms,
	}
)


h2Transiton_2 = ( # 2 H Wanderung charge
	"[C.]2([H]3)[C]4[_Y_1]5[C]6([C]7){=}[_Y_2+]8[H]1" +
	">>" +
	"[C.]2([H]3)[C]4[_Y_1+]5{=}[C]6([C]7)[_Y_2]8[H]1",
	"2 H transition charge"
)

h2Transiton_2 = convert2MoelRule(h2Transiton_2)

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

h2Transiton_3 = convert2MoelRule(h2Transiton_3)

h2Transiton_3 = labelConstraints_gml(
	input_rules = h2Transiton_3,
	rpl_dict = {
		"_Y_1": heteroAtoms,
		"_Y_2": heteroAtoms,
	}
)