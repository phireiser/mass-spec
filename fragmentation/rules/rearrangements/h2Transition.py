h2Transiton_1 = Rule.fromDFS(# 2 H-migr. rH
	s=
	"[H]1[C]2([H]3)[C]4[*]5[C]6([C]7){=}[*+.]8" +
	">>" +
	"[C.]2([H]3)[C]4[*]5[C]6([C]7){=}[*+]8[H]1", 
	name= 
	"2 H transition rH1" +
	" §Y5Y8"
)

h2Transiton_2 = Rule.fromDFS(# 2 H-migr. charge
	s=
	"[C.]2([H]3)[C]4[*]5[C]6([C]7){=}[*+]8[H]1" +
	">>" +
	"[C.]2([H]3)[C]4[*+]5{=}[C]6([C]7)[*]8[H]1",
	name = 
	"2 H transition charge" +
	" §Y5Y8"
)

h2Transiton_3 = Rule.fromDFS( # 2 H-migr. split
	s=
	"[C.]2([H]3)[C]4[*]5[C]6([C]7){=}[*+]8[H]1" +
	">>" +
	"[C]2{=}[C]4.[H]3[*+]5{=}[C]6([C]7)[*]8[H]1",
	name =
	"2 H transition rH2 split" +
	" §Y5Y8"
)