hTransition_saturated_1 = Rule.fromDFS(
	s =
	"[H]1[C]2[C]3.[C]4[O+.]5[C]6" +
	">>" +
	"[C.]2[C]3.[C]4[O+]5([H]1)([C]6)",
	name =
	"H transition receptor site saturated" +
	" ^S3-4Y5R6"
)

hTransition_saturated_1_alpha = Rule.fromDFS(
	s =
	"[C.]1[C]2.[C]3[O+]4([H]5)([C]6)" +
	">>" +
	"[C]1[C]2.[C]3{-}1.[O+.]4([H]5)([C]6)",
	name =
	"H transition receptor site saturated" +
	" ^S2-3Y4R6"
)

hTransition_saturated_1_inductive_1 = Rule.fromDFS(
	s =
	"[C.]1[C]2.[C]3[O+]4([H]5)([C]6)" +
	">>" +
	"[C.]1[C]2.[C+]3.[O+.]4([H]5)([C]6)",
	name =
	"H transition receptor site saturated" +
	" ^S2-3Y4R6"
)

hTransition_saturated_1_inductive_2 = Rule.fromDFS(
	s = 
	"[C.]1[C]2.[C]3[O+]4([H]5)([C]6)" +
	">>" +
	"[C]1[C]2.[C+.]3{-}1.[O+.]4([H]5)([C]6)",
	name = 
	"H transition receptor site saturated inductive" +
	" ^S2-3Y4R6"
)

hTransition_saturated_2 = Rule.fromDFS( # siehe 8.53
	s = 
	"[H]1[C]2[C]3([O+]4).[C]5[C.]6" +
	">>" +
	"[O+]4[C.]2[C]3.[C]5([H]1)[C]6",
	name =
	"H transition receptor site saturated rH" +
	" ^Y4S3-5"
)

hTransition_saturated_2_alpha = Rule.fromDFS( # siehe 8.53
	s =
	"[O+]1[C.]2[C]3([H]4).[C]5" +
	">>" +
	"[O+.]1.[C]2([H]4)[C]3.[C]5{-}1",
	name =
	"H transition receptor site saturated alpha" +
	" ^Y1S3-5"
)

hTransition_saturated_3 = Rule.fromDFS( # siehe 4.44 & 4.46
	s = 
	"[H]1[C]2[C]3.[C]4[O+]5{=}[C]6([H]7)([C]8)" +
	">>" +
	"[C.]2[C]3.[C]4[O+]5([H]1){=}[C]6([H]7)([C]8)",
	name =
	"H transition receptor site saturated rH" +
	" ^S3-4Y5R8"
)

hTransition_saturated_3_alpha = Rule.fromDFS( # siehe 4.44 & 4.46
	s =
	"[C.]1[C]2.[C]3[O+]4([H]5){=}[C]6([H]7)([C]8)" +
	">>" +
	"[C]1[C]2.[C]3{-}1.[O+.]4([H]5){=}[C]6([H]7)([C]8)",
	name =
	"H transition receptor site saturated alpha" + 
	" ^S2-3Y4R8"
)

hTransition_saturated_4 = Rule.fromDFS( # siehe 8.90
	s =
	"[H]1[C]2[C]3.[C]4([H]5){=}[O+]6[C]7" +
	">>" +
	"[C.]2[C]3.[C]4([H]5)([H]1){=}[O+]6[C]7",
	name =
	"H transition receptor site saturated rH" +
	" ^Y7S3-4R8"
)

hTransition_saturated_4_alpha = Rule.fromDFS( # siehe 8.90
	s =
	"[C.]1[C]2[C]3[C]4([H]5)([H]6){=}[O+]7[C]8" +
	">>" +
	"[C]1[C]2[C]3{-}1.[C]4([H]5)([H]6){=}[O+.]7[C]8",
	name =
	"H transition receptor site saturated alpha"
)

hTransition_saturated_5 = Rule.fromDFS( # siehe 4.45
	s = 
	"[H]1[C]2([O+]3)[C]4[C]5[O..]6[C]7" +
	">>" +
	"[C]2([O+]3)[C]4[C]5[O..]6([H]1)[C]7",
	name =
	"H transition receptor site saturated rH" +
	" ^Y6S2-4Y3R7"
)

hTransition_saturated_5_inductive_1 = Rule.fromDFS( # siehe 4.45
	s =
	"[C]1([O+]2).[C]3[C]4[O..]5([H]6)[C]7" +
	">>" +
	"[C.]1([O+]2).[C]3[C+]4[O+.]5([H]6)[C]7",
	name =
	"H transition receptor site saturated inductive" +
	" ^Y2S1-3Y5R7"
)

hTransition_saturated_5_inductive_2 = Rule.fromDFS( # siehe 4.45
	s = 
	"[C.]1([O+]2).[C]3[C+]4[O+.]5([H]6)[C]7" +
	">>" +
	"[C.]1([O+]2).[C]3[C+]4.[O.]5([H]6)[C]7",
	name = 
	"H transition receptor site saturated inductive" +
	" ^Y2S1-3Y5R7"
)

hTransition_saturated_5_inductive_3 = Rule.fromDFS( # siehe 4.45
	s =
	"[C.]1([O+]2).[C]3[C+]4[O+.]5([H]6)[C]7" +
	">>" +
	"[C]1([O+]2).[C]3[C+.]4{-}1.[O.]5([H]6)[C]7",
	name = 
	"H transition receptor site saturated inductive" +
	" ^Y2S1-3Y5R7"
)