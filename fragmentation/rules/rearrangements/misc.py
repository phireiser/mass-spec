IMS_4_33_rH = Rule.fromDFS(
	s = 
	"[C]1[C]2([H]3)[C]4[C]5[C]6([C]7){=}[O+.]8" +
	">>" +
	"[C]1[C.]2[C]4[C]5[C]6([C]7){=}[O+]8[H]3",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage" + 
    " 4.33 rH" +
	" ^R1"
)

IMS_4_33_alpha_1 = Rule.fromDFS(
	s = 
	"[C]1[C.]2[C]3[C]4[C]5([C]6){=}[O+]7[H]8" +
	">>" +
	"[C]1[C]2{=}[C]3.[C.]4[C]5([C]6){=}[O+]7[H]8",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage" + 
    " 4.33 alpha 1" +
	" ^R1"
)


IMS_4_33_alpha_2 = Rule.fromDFS(
	s = 
	"[C]1[C.]2[C]3[C]4[C]5([C]6){=}[O+]7[H]8" +
	">>" +
	"[C]1[C]2{=}[C]3.[C.]4{=}[C]5([C]6)[O+.]7[H]8",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage" + 
    " 4.33 alpha 2" +
	" ^R1"
)

IMS_4_34_rH = Rule.fromDFS(
	s = 
	"[C]1[C]2([H]3)[C]4[C]5[C]6([C]7){=}[O+.]8" +
	">>" +
	"[C]1[C.]2[C]4[C]5[C+]6([C]7)[O]8[H]3",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage" + 
    " 4.34 rH" +
	" ^R1"
)

IMS_4_34_ind = Rule.fromDFS(
	s = 
	"[C]1[C.]2[C]3[C]4[C+]5([C]6)[O]7[H]8" +
	">>" +
	"[C]1[C.]2[C+]3.[C]4{=}[C]5([C]6)[O]7[H]8",
	name=
    "gamma H Wanderung to unsaturated group with beta cleavage" +
    " 4.34 inductive" +
	" ^R1"
)

IMS_4_35_rHalpha = Rule.fromDFS(
	s = 
	"[C]1[C]2([H]3)[C]4[C]5[C]6{=}[N+.]8[N]9([C]10)[C]11" +
	">>" +
	"[C]1[C]2{=}[C]4.[C.]5[C]6{=}[N+]8([H]3)[N]9([C]10)[C]11",
	name=
    "gamma H Wanderung to unsaturated group Odd electron Ion" +
    " 4.35 rH alpha" +
	""
)

IMS_4_36_ = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C]7{=}[C]8[C]9{=}[C]10[C]11{=}[C]12{-}7" + # ring has somewhere a radical ion +.
	">>" +
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C+]7[C.]8[C]9{=}[C]10[C]11{=}[C]12{-}7",
	name=
    "gamma H Wanderung to unsaturated group Odd electron Ion" + 
    " 4.36 charge move" +
	""
)

IMS_4_36__rHalpha = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C+]7[C.]8[C]9{=}[C]10[C]11{=}[C]12{-}7" +
	">>" +
	"[C]1[C]2[C]3{=}[C]5.[C.]6[C+]7[C]8([H]4)[C]9{=}[C]10[C]11{=}[C]12{-}7",
	name=
    "gamma H Wanderung to unsaturated group Odd electron Ion" + 
    " 4.36 rH alpha" +
	""
)

IMS_4_37_rH = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3([H]4)[C]5[C]6[C]7[O+.]8[H]9" +
    ">>" +
    "[C]1[C]2[C.]3[C]5[C]6[C]7[O+]8([H]4)[H]9",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.37 rH" +
    ""
)

IMS_4_37_rd = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6[O+]7([H]8)[H]9" +
    ">>" +
    "[C]1[C]2[C]3[C]4[C]5[C]6{-}3.[O+.]7([H]8)[H]9",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.37 rd" +
    ""
)

IMS_4_38_rH = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3([H]4)[C]5[C]6[C]7[O+.]8[H]9" +
    ">>" +
    "[C]1[C]2[C.]3[C]5[C]6[C]7[O+]8([H]4)[H]9",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.38 rH" +
    ""
)

IMS_4_38_ind = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6[O+]7([H]8)[H]9" +
    ">>" +
    "[C]1[C]2[C.]3[C]4[C]5[C+]6.[O]7([H]8)[H]9",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.38 ind" +
    ""
)

IMS_4_38_ind_2 = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C+]6" +
    ">>" +
    "[C]1[C]2[C.]3[C+]4.[C]5{=}[C]6",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.38 ind" +
    ""
)

IMS_4_39_rH = Rule.fromDFS(
    s =
    "[C]1([H]2)[C]3({=}[O]4)[N+.]5([H]6)[C]7[C]8[C]9[C]10" +
    ">>" +
    "[C.]1[C]3({=}[O]4)[N+]5([H]2)([H]6)[C]7[C]8[C]9[C]10",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.39 rH" +
    ""
)

IMS_4_39_alpha = Rule.fromDFS(
    s =
    "[C.]1[C]2({=}[O]3)[N+]4([H]5)([H]6)[C]7[C]8[C]9[C]10" +
    ">>" +
    "[C]1{=}[C]2{=}[O]3.[N+.]4([H]5)([H]6)[C]7[C]8[C]9[C]10",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.39 alpha" +
    ""
)

IMS_4_40_rH = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3([H]4)[C]5[C]6[Cl+.]7" +
    ">>" +
    "[C]1[C]2[C.]3[C]5[C]6[Cl+]7[H]4",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.40 rH" +
    ""
)

IMS_4_40_ind = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[Cl+]6[H]7" +
    ">>" +
    "[C]1[C]2[C]3[C]4[C+.]5{-}3.[Cl]6[H]7", # charge somewhere in cycle
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.40 ind" +
    ""
)

IMS_4_41_rH = Rule.fromDFS(
    s =
    "[H]1[Cl]2[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8({=}3)[C]9({=}[O]10)[O+.]11[C]12" +
    ">>" +
    "[Cl.]2[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8({=}3)[C]9({=}[O]10)[O+]11([H]1)[C]12",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.41 rH" +
    " ^Y2R12"
)

IMS_4_41_ind1 = Rule.fromDFS(
    s =
    "[Cl.]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({=}2)[C]8({=}[O]9)[O+]10([H]11)[C]12" +
    ">>" +
    "[Cl.]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({=}2)[C]8{#}[O+]9.[O]10([H]11)[C]12",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.41 ind prod 1" +
    " ^Y1R12"
)

IMS_4_41_ind2 = Rule.fromDFS(
    s =
    "[Cl.]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({=}2)[C]8({=}[O]9)[O+]10([H]11)[C]12" +
    ">>" +
    "[Cl]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({-}2){=}[C]8{=}[O+]9.[O]10([H]11)[C]12",
    name =
    "H-Wanderung to a unsatturated hetroatom and clevage of neighbouring bond" +
    " 4.41 ind prod 2" +
    " ^Y1R12"
)

IMS_4_42_rd = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3[C]4[C]5[Cl+.]6" +
    ">>" +
    "[C.]1.[C]2[C]3[C]4[C]5[Cl+]6{-}2",
    name =
    "displacement reaction" +
    " 4.42 rd" +
    " ^R1"
)

IMS_4_43_ = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[N+.]8([H]9)[C]10([H]11)([H]12)[C]13([H]14)([H]15)[H]16" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[N+]8([H]9){=}[C]10([H]11)([H]12).[C.]13([H]14)([H]15)[H]16",
    name =
    "displacement reaction" +
    " 4.43" +
    ""
)

IMS_4_43_rH = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[N+]8([H]9){=}[C]10([H]11)([H]12)" +
    ">>" +
    "[C]1([H]2)([H]3){=}[C]5([H]6)([H]7).[N+]8([H]4)([H]9){=}[C]10([H]11)([H]12)",
    name =
    "displacement reaction" +
    " 4.43 rH" +
    ""
)

IMS_4_44_ind = Rule.fromDFS(
    s =
    "[Cl+.]1[C]2([C]3([H]4)([H]5)([H]6))([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[Cl]14" +
    ">>" +
    "[Cl.]1.[C]3([H]4)([H]5)([H]6)[C+]2([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[Cl..]14",
    name =
    "displacement reaction" +
    " 4.44 ind" +
    ""
)

IMS_4_44_rH = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C+]5([H]6)[C]7([H]8)([H]9)[C]10([H]11)([H]12)[Cl..]13" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C+]5([H]6)[C]7([H]8){=}[C]10([H]11)([H]12).[Cl]13[H]9",
    name =
    "displacement reaction" +
    " 4.44 rH" +
    ""
)

IMS_4_45_rH = Rule.fromDFS(
    s =
    "[C]1[C]2([H]3)[C]4[O]5[C]6([C]7){=}[O+.]8" +
    ">>" +
    "[C]1[C.]2[C]4[O]5[C]6([C]7){=}[O+]8[H]3",
    name =
    "displacement reaction" +
    " 4.45 rH" +
    " ^R1R7"
)

IMS_4_45_alpha = Rule.fromDFS(
    s =
    "[C]1[C.]2[C]3[O]4[C]5([C]6){=}[O+]7[H]8" +
    ">>" +
    "[C]1[C]2[C]3.[O+.]4{=}[C]5([C]6)[O+]7[H]8",
    name =
    "displacement reaction" +
    " 4.45 alpha" +
    " ^R1R6"
)

IMS_4_46_rH_1 = Rule.fromDFS(
    s =
    "[H]1[C]2[C]3([H]4)[C]5[O]6[C]7([C]8){=}[O+.]9" +
    ">>" +
    "[H]1[C]2[C.]3[C]5[O+]6[C]7([C]8){=}[O]9[H]4",
    name =
    "displacement reaction" +
    " 4.46 rH" +
    " ^R2R8"
)

IMS_4_46_rH_2 = Rule.fromDFS(
    s =
    "[H]1[C]2[C.]3[C]4[O]5[C]6([C]7){=}[O]8[H]9" +
    ">>" +
    "[C]2[C.]3[C]4.[H]1[O+]5{=}[C]6([C]7)[O]8[H]9", # radical anywhere on first fragment
    name =
    "displacement reaction" +
    " 4.46 rH2 var 1" +
    " ^R2R7"
)

IMS_4_46_rH_2_ = Rule.fromDFS(
    s =
    "[H]1[C]2[C.]3[C]4[O]5[C]6([C]7){=}[O]8[H]9" +
    ">>" +
    "[C]2[C.]3[C]4.[H]1[O+]5[C]6([C]7){=}[O+]8[H]9", # radical anywhere on first fragment
    name =
    "displacement reaction" +
    " 4.46 rH2 var 2" +
    " ^R2R7"
)