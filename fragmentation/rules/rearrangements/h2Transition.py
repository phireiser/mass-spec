h2Transiton_1 = Rule.fromDFS(# 2 H Wanderung rH
	s=
	"[H]1[C]2([H]3)[C]4[O]5[C]6([C]7){=}[O+.]8" +
	">>" +
	"[C.]2([H]3)[C]4[O]5[C]6([C]7){=}[O+]8[H]1", 
	name= 
	"2 H transition rH1" +
	" ^Y5Y8"
)

h2Transiton_2 = Rule.fromDFS(# 2 H Wanderung charge
	s=
	"[C.]2([H]3)[C]4[O]5[C]6([C]7){=}[O+]8[H]1" +
	">>" +
	"[C.]2([H]3)[C]4[O+]5{=}[C]6([C]7)[O]8[H]1",
	name = 
	"2 H transition charge" +
	" ^Y5Y8"
)

h2Transiton_3 = Rule.fromDFS( # 2 H Wanderung split
	s=
	"[C.]2([H]3)[C]4[O]5[C]6([C]7){=}[O+]8[H]1" +
	">>" +
	"[C]2{=}[C]4.[H]3[O+]5{=}[C]6([C]7)[O]8[H]1",
	name =
	"2 H transition rH2 split" +
	" ^Y5Y8 "
)