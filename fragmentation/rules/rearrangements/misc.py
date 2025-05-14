IMS_4_33_rH = Rule.fromDFS(
	s = 
	"[R]1[C]2([H]3)[C]4[C]5[C]6([C]7){=}[O+.]8" +
	">>" +
	"[R]1[C.]2[C]4[C]5[C]6([C]7){=}[O+]8[H]3",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage 4.33 rH" +
	" ^R1"
)

IMS_4_33_alpha_1 = Rule.fromDFS(
	s = 
	"[R]1[C.]2[C]3[C]4[C]5([C]6){=}[O+]7[H]8" +
	">>" +
	"[R]1[C]2{=}[C]3.[C.]4[C]5([C]6){=}[O+]7[H]8",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage 4.33 alpha 1" +
	" ^R1"
)


IMS_4_33_alpha_2 = Rule.fromDFS(
	s = 
	"[R]1[C.]2[C]3[C]4[C]5([C]6){=}[O+]7[H]8" +
	">>" +
	"[R]1[C]2{=}[C]3.[C.]4{=}[C]5([C]6)[O+.]7[H]8",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage 4.33 alpha 2" +
	" ^R1"
)



IMS_4_34_rH = Rule.fromDFS(
	s = 
	"[R]1[C]2([H]3)[C]4[C]5[C]6([C]7){=}[O+.]8" +
	">>" +
	"[R]1[C.]2[C]4[C]5[C+]6([C]7)[O]8[H]3",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage 4.34 rH" +
	" ^R1"
)

IMS_4_34_ind = Rule.fromDFS(
	s = 
	"[R]1[C.]2[C]3[C]4[C+]5([C]6)[O]7[H]8" +
	">>" +
	"[R]1[C.]2[C+]3.[C]4{=}[C]5([C]6)[O]7[H]8",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage 4.34 inductive" +
	" ^R1"
)

IMS_4_35_rHalpha = Rule.fromDFS(
	s = 
	"[C]1[C]2([H]3)[C]4[C]5[C]6{=}[N+.]8[N]9([C]10)[C]11" +
	">>" +
	"[C]1[C]2{=}[C]4.[C.]5[C]6{=}[N+]8([H]3)[N]9([C]10)[C]11",
	name=
    "gamma H Wanderung to unsaturated group Odd electron Ion 4.35 rH alpha" +
	""
)


IMS_4_36_ = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C]7{=}[C]8[C]9{=}[C]10[C]11{=}[C]12{-}7" + # ring has somewhere a radical ion +.
	">>" +
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C+]7[C.]8[C]9{=}[C]10[C]11{=}[C]12{-}7",
	name=
    "gamma H Wanderung to unsaturated group Odd electron Ion 4.36 charge move" +
	""
)

IMS_4_36__rHalpha = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C+]7[C.]8[C]9{=}[C]10[C]11{=}[C]12{-}7" +
	">>" +
	"[C]1[C]2[C]3{=}[C]5.[C.]6[C+]7[C]8([H]4)[C]9{=}[C]10[C]11{=}[C]12{-}7",
	name=
    "gamma H Wanderung to unsaturated group Odd electron Ion 4.36 rH alpha" +
	""
)
