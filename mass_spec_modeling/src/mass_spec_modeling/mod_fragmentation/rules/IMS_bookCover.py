import mod


# Interpreation von Massenspektren Springer, Einband Seiten

#IMS_4_7

# element with low IE
sigma_lowIE = mod.Rule.fromDFS( 
	s =
	"[_A+.]1[I]2"
	">>"
	"[_A.]1" "." "[I+]2",
	name =
	"dissoziation of a sigma bond for Elements with low IE"
	" §R1"
)

#IMS_4_9 gesattigte Stelle

#IMS_4_10 gesattigte Stelle

#IMS_4_11 ungesaettigtes Heteroatom

#IMS_4_12 Alkene (Allylspaltung)


#IMS_4_31 Retro-Diels-Alder

#IMS_4_32 Retro-Diels-Alder


#IMS_4_18 OE+. hetrolytische Dissioziation

#IMS_4_20 EE+. hetrolytische Dissioziation


####### h Transtion unsaturated

hTransition_unsaturated = mod.Rule.fromDFS(
	s =
	"[H]1[C]2[C]3[C]4[C]5{=}[_A+.]6"
	">>"
	"[C.]2[C]3[C]4[C]5{=}[_A+]6[H]1", 
	name = 
	"H transition receptor site unsaturated"
	" §Y6"
)

hTransition_unsaturated_alpha = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2[C]3[C]4{=}[_A+]5[H]6"
	">>"
	"[C]1{=}[C]2" "." "[C.]3[C]4{=}[_A+]5[H]6",
	name = 
	"H transition receptor site unsaturated"
	" §Y5"
)

hTransition_unsaturated_bidirect = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2[C]3[C]4{=}[_A+]5[H]6"
	">>"
	"[C.]1[C]2[C]3[C+]4[_A]5[H]6", 
	name = 
	"H transition receptor site unsaturated"
	" §Y5"
)

hTransition_unsaturated_inductive = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2[C]3[C]4{=}[_A+]5[H]6"
	">>"
	"[C.]1[C+]2" "." "[C]3{=}[C]4[_A]5[H]6", 
	name = 
	"H transition receptor site unsaturated"
	" §Y5"
)

####### hTranstion saturated

hTransition_saturated_1 = mod.Rule.fromDFS(
	s =
	"[H]1[C]2[C]3" "." "[C]4[_A+.]5" #YRY "[H]1[C]2[C]3.[C]4[_A+.]5[_A]6" 
	">>"
	"[C.]2[C]3" "." "[C]4[_A+]5([H]1)", #YRY "[C.]2[C]3.[C]4[_A+]5([H]1)([_A]6)"
	name =
	"H transition receptor site saturated"
	" §S3-4Y5" #YRY " §S3-4Y5R6" 
)

hTransition_saturated_1_alpha = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2" "." "[C]3[_A+]4([H]5)" #YRY "[C.]1[C]2.[C]3[_A+]4([H]5)([_A]6)"
	">>"
	"[C]1[C]2" "." "[C]3{-}1.[_A+.]4([H]5)", #YRY "[C]1[C]2.[C]3{-}1.[_A+.]4([H]5)([_A]6)"
	name =
	"H transition receptor site saturated"
	" §S2-3Y4" # YRY " §S2-3Y4R6"
)

hTransition_saturated_1_inductive_1 = mod.Rule.fromDFS(
	s =
	"[C.]1[C]2" "." "[C]3[_A+]4([H]5)" #YRY "[C.]1[C]2.[C]3[_A+]4([H]5)([_A]6)"
	">>"
	"[C.]1[C]2" "." "[C+]3.[_A+.]4([H]5)", #YRY "[C.]1[C]2.[C+]3.[_A+.]4([H]5)([_A]6)"
	name =
	"H transition receptor site saturated"
	" §S2-3Y4" #YRY " §S2-3Y4R6"
)

hTransition_saturated_1_inductive_2 = mod.Rule.fromDFS(
	s = 
	"[C.]1[C]2.[C]3[_A+]4([H]5)" #YRY "[C.]1[C]2.[C]3[_A+]4([H]5)([_A]6)"
	">>"
	"[C]1[C]2" "." "[C+.]3{-}1" "." "[_A+.]4([H]5)", #YRY "[C]1[C]2.[C+.]3{-}1.[_A+.]4([H]5)([_A]6)"
	name = 
	"H transition receptor site saturated inductive"
	" §S2-3Y4" #YRY " §S2-3Y4R6"
)

hTransition_saturated_2 = mod.Rule.fromDFS( # siehe 8.53
	s = 
	"[H]1[C]2[C]3([_A+]4)" "." "[C]5[C.]6"
	">>"
	"[_A+]4[C.]2[C]3" "." "[C]5([H]1)[C]6",
	name =
	"H transition receptor site saturated rH"
	" §Y4S3-5"
)

hTransition_saturated_2_alpha = mod.Rule.fromDFS( # siehe 8.53
	s =
	"[_A+]1[C.]2[C]3([H]4)" "." "[C]5"
	">>"
	"[_A+.]1" "." "[C]2([H]4)[C]3" "." "[C]5{-}1",
	name =
	"H transition receptor site saturated alpha"
	" §Y1S3-5"
)

hTransition_saturated_3 = mod.Rule.fromDFS( # siehe 4.44 & 4.46
	s = 
	"[H]1[C]2[C]3" "." "[C]4[_A+]5{=}[C]6([H]7)([_A]8)"
	">>"
	"[C.]2[C]3" "." "[C]4[_A+]5([H]1){=}[C]6([H]7)([_A]8)",
	name =
	"H transition receptor site saturated rH"
	" §S3-4Y5R8"
)

hTransition_saturated_3_alpha = mod.Rule.fromDFS( # siehe 4.44 & 4.46
	s =
	"[C.]1[C]2" "." "[C]3[_A+]4([H]5){=}[C]6([H]7)([_A]8)"
	">>"
	"[C]1[C]2" "." "[C]3{-}1" "." "[_A+.]4([H]5){=}[C]6([H]7)([_A]8)",
	name =
	"H transition receptor site saturated alpha" 
	" §S2-3Y4R8"
)

hTransition_saturated_4 = mod.Rule.fromDFS( # siehe 8.90
	s =
	"[H]1[C]2[C]3" "." "[C]4([H]5){=}[_A+]6" #YRY "[H]1[C]2[C]3.[C]4([H]5){=}[_A+]6[_A]7"
	">>"
	"[C.]2[C]3" "." "[C]4([H]5)([H]1){=}[_A+]6", #YRY "[C.]2[C]3.[C]4([H]5)([H]1){=}[_A+]6[_A]7"
	name =
	"H transition receptor site saturated rH"
	" §Y6S3-4" #YRY " §Y6S3-4R7"
)

hTransition_saturated_4_alpha = mod.Rule.fromDFS( # siehe 8.90
	s =
	"[C.]1[C]2[C]3[C]4([H]5)([H]6){=}[O+]7[C]8"
	">>"
	"[C]1[C]2[C]3{-}1" "." "[C]4([H]5)([H]6){=}[O+.]7[C]8",
	name =
	"H transition receptor site saturated alpha"
	"" #TODO no rule enhancemend?
)

hTransition_saturated_5 = mod.Rule.fromDFS( # siehe 4.45
	s = 
	"[H]1[C]2([_A+]3)[C]4[C]5[_A..]6" #YRY "[H]1[C]2([_A+]3)[C]4[C]5[_A..]6[_A]7"
	">>"
	"[C]2([_A+]3)[C]4[C]5[_A..]6([H]1)", #YRY "[C]2([_A+]3)[C]4[C]5[_A..]6([H]1)[_A]7"
	name =
	"H transition receptor site saturated rH"
	" §Y6S2-4Y3" #YRY " §Y6S2-4Y3R7"
)

hTransition_saturated_5_inductive_1 = mod.Rule.fromDFS( # siehe 4.45
	s =
	"[C]1([_A+]2)" "." "[C]3[C]4[_A..]5([H]6)" #YRY "[C]1([_A+]2).[C]3[C]4[_A..]5([H]6)[_A]7"
	">>"
	"[C.]1([_A+]2)" "." "[C]3[C+]4[_A+.]5([H]6)", #YRY "[C.]1([_A+]2).[C]3[C+]4[_A+.]5([H]6)[_A]7"
	name =
	"H transition receptor site saturated inductive"
	" §Y2S1-3Y5" #YRY " §Y2S1-3Y5R7"
)

hTransition_saturated_5_inductive_2 = mod.Rule.fromDFS( # siehe 4.45
	s = 
	"[C.]1([_A+]2)" "." "[C]3[C+]4[_A+.]5([H]6)" #YRY "[C.]1([_A+]2).[C]3[C+]4[_A+.]5([H]6)[_A]7"
	">>"
	"[C.]1([_A+]2)" "." "[C]3[C+]4.[_A.]5([H]6)", #YRY "[C.]1([_A+]2).[C]3[C+]4.[_A.]5([H]6)[_A]7"
	name = 
	"H transition receptor site saturated inductive"
	" §Y2S1-3Y5" #YRY " §Y2S1-3Y5R7"
)

hTransition_saturated_5_inductive_3 = mod.Rule.fromDFS( # siehe 4.45
	s =
	"[C.]1([_A+]2)" "." "[C]3[C+]4[_A+.]5([H]6)" #YRY "[C.]1([_A+]2).[C]3[C+]4[_A+.]5([H]6)[_A]7"
	">>"
	"[C]1([_A+]2)"
	"."
	"[C]3[C+.]4{-}1"
	"."
	"[_A.]5([H]6)", #YRY "[C]1([_A+]2).[C]3[C+.]4{-}1.[_A.]5([H]6)[_A]7"
	name = 
	"H transition receptor site saturated inductive"
	" §Y2S1-3Y5" #YRY " §Y2S1-3Y5R7"
)

####### h2Transiton

h2Transiton_1 = mod.Rule.fromDFS(# 2 H-migr. rH 4.46
	s=
	"[H]1[C]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+.]8"
	">>"
	"[C.]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+]8[H]1", 
	name= 
	"2 H transition rH1"
	" §Y5Y8"
)

h2Transiton_2 = mod.Rule.fromDFS(# 2 H-migr. charge 4.46
	s=
	"[C.]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+]8[H]1"
	">>"
	"[C.]2([H]3)[C]4[_A+]5{=}[C]6([C]7)[_A]8[H]1",
	name = 
	"2 H transition charge"
	" §Y5Y8"
)

h2Transiton_3 = mod.Rule.fromDFS( # 2 H-migr. split 4.46
	s=
	"[C.]2([H]3)[C]4[_A]5[C]6([C]7){=}[_A+]8[H]1"
	">>"
	"[C]2{=}[C]4"
	"."
	"[H]3[_A+]5{=}[C]6([C]7)[_A]8[H]1",
	name =
	"2 H transition rH2 split"
	" §Y5Y8"
)

####### substituion

substituion = mod.Rule.fromDFS( # siehe 4.42
	s =
	"[_A]1[C]2.[C]3[_A+.]4" #YRY "[_A]1[C]2.[C]3[_A+.]4[_A]5"
	">>"
	"[_A.]1"
	"."
	"[C]2.[C]3[_A+]4{-}2", #YRY "[_A.]1.[C]2.[C]3[_A+]4([_A]5){-}2"
	name=
	"Substituion"
	" §R1S2-3Y4" #YRY " §R1S2-3Y4R5"
)

####### elimination

elimination = mod.Rule.fromDFS( # siehe Tab. 8.4
	"[_A]1[C]2.[C]3[_A+]4[_A]5"
	">>"
	"[C]2"
	"."
	"[C]3{-}2.[_A]1[_A]4[_A+]5",
	name = 
	"Elimination"
	" §R1S2-3R4Y5"
)



rearrangements = [
	hTransition_unsaturated,
	hTransition_unsaturated_alpha,
	hTransition_unsaturated_bidirect,
	hTransition_unsaturated_inductive,

	hTransition_saturated_1,
	hTransition_saturated_1_alpha,
	hTransition_saturated_1_inductive_1,
	hTransition_saturated_1_inductive_2,

	hTransition_saturated_2,
	hTransition_saturated_2_alpha,

	hTransition_saturated_3,
	hTransition_saturated_3_alpha,

	hTransition_saturated_4,
	hTransition_saturated_4_alpha,

	hTransition_saturated_5_inductive_1,
	hTransition_saturated_5_inductive_2,
	hTransition_saturated_5_inductive_3,

	h2Transiton_1,
	h2Transiton_2,
	h2Transiton_3,
	substituion,
	elimination,
]


IMS_cover_fragmentation = [
    sigma_lowIE,
]

IMS_cover_fragmentation.extend(rearrangements)