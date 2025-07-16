# Interpreation von Massenspektren Springer, Seite 56, Gl. 4.3
IMS_4_3_var1 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C+.]5([H]6)([H]7)[C]8([H]9)([H]10)([H]11)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C+]5([H]6)([H]7).[C.]8([H]9)([H]10)([H]11)",
    name =
    "one bond cleavage" +
	" 4.3 var1" +
	""
)

IMS_4_3_var2 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C+.]5([H]6)([H]7)[C]8([H]9)([H]10)([H]11)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)([H]7).[C+]8([H]9)([H]10)([H]11)",
    name =
    "one bond cleavage" +
	" 4.3 var2" +
	""
)

# Interpreation von Massenspektren Springer, Seite 56, Gl. 4.4
IMS_4_4_row1 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)[C]4([H]5)[O+.]6([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13){-}1" +
	">>" +
	"[C]1([H]2)([H]3){=}[C]4([H]5)[O+.]6([H]7).[C]8([H]9)([H]10){=}[C]11([H]12)([H]13)",
	name =
	"charge conservation" +
	" 4.4 row 1" +
	""
)

IMS_4_4_row2 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)[C]4([H]5)[O+.]6([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13){-}1" +
	">>" +
	"[C]1([H]2)([H]3){=}[C]4([H]5)[O]6([H]7).[C]8([H]9)([H]10){=}[C+.]11([H]12)([H]13)",
	name =
	"charge transfer" +
	" 4.4 row 2" +
	""
)

IMS_4_4_row3 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[O+.]8([H]9)" +
	">>" +
	"[C]1([H]2)([H]3){=}[C]5([H]6)([H]4).[H]7[O+.]8[H]9",
	name =
	"charge conseration var 2" +
	" 4.4 row 3" +
	""
)

IMS_4_4_row4 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[O+.]8([H]9)" +
	">>" +
	"[C]1([H]2)([H]3){=}[C+.]5([H]6)([H]4).[H]7[O]8[H]9",
	name =
	"charge transfer var 2" +
	" 4.4 row 4" +
	""
)

# Interpreation von Massenspektren Springer, Seite 56, Gl. 4.5
IMS_4_5 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7){-}[C+.]8([H]10)([H]11)[C]12([H]13)([H]14)([H]15)" + #charge radical somewhere
	">>" +
	"[C]1([H]2)([H]3)([H]4)[C.]5([H]6)([H]7).[C+]8([H]10)([H]11)[C]12([H]13).[H]14[H]15",
	name =
	"cleavage of 3 bonds" +
	" 4.5" +
	""
)

# Interpreation von Massenspektren Springer, Seite 56, Gl. 4.6
IMS_4_6_row1 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7){-}[O+]8{=}[C]9([H]10)([H]11)" +
	">>" +
	"[C]1([H]2)([H]3)([H]4)[C+]5([H]6)([H]7).[O]8{=}[C]9([H]10)([H]11)",
	name =
	"rule of uneven elektron counts" +
	" 4.6 row 1" +
	""
)

IMS_4_6_row2 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7){-}[O+]8{=}[C]9([H]10)([H]11)" +
	">>" +
	"[C]1([H]2)([H]3){=}[C+]5([H]6)([H]4).[H]7[O+]8{=}[C]9([H]10)([H]11)",
	name =
	"rule of uneven elektron counts" +
	" 4.6 row 2" +
	""
)

IMS_4_6_row3 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7){-}[O+]8{=}[C]9([H]10)([H]11)" +
	">>" +
	"[C]1([H]2)([H]3)([H]4)[C.]5([H]6)([H]7).[O]8{=}[C+.]9([H]10)([H]11)",
	name =
	"rule of uneven elektron counts" +
	" 4.6 row 3" +
	""
)

IMS_4_6_row4 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)[C+]4([H]5)[C]6([H]7)([H]8)[C]9([H]10)([H]11){-}1" +
	">>" +
	"[C]1([H]2)([H]3){=}[C+]4([H]5).[C]6([H]7)([H]8){=}[C]9([H]10)([H]11)",
	name =
	"rule of uneven elektron counts" +
	" 4.4 row 4" +
	""
)

IMS_4_6_row5 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)[C]4([H]5)[C]6([H]7)([H]8)[C]9([H]10)([H]11){-}1" +
	">>" +
	"[C]1([H]2)([H]3)[C.]4([H]5)[C]6([H]7)([H]8)[C+.]9([H]10)([H]11)",
	name =
	"rule of uneven elektron counts" +
	" 4.6 row 5" +
	""
)

# Interpreation von Massenspektren Springer, Seite 58, Gl. 4.7 und Seite Einband
IMS_4_7 = Rule.fromDFS(
	s = 
	"[C+.]1[C]2[C]3[C]4[C]5" +
	">>" +
	"[C.]1.[C+]2[C]3[C]4[C]5",
	name = 
	"dissoziation of a sigma bond for alkans" +
	" 4.7" +
	" §R1R3R4R5"
	
)

# Interpreation von Massenspektren Springer, Seite 59, Gl. 4.8
IMS_4_8 = Rule.fromDFS(
	s =
	"[C+.]1" +
	"([C]2([H]3)([H]4)([H]5))" +
	"([C]6([H]7)([H]8)([H]9))" +
	"([C]10([H]11)([H]12)([H]13))" +
	"[C]14([H]15)([H]16)" +
	"[C]20([H]21)([H]22)([H]23)" +
	">>" +
	"[C+]1" +
	"([C]2([H]3)([H]4)([H]5))" +
	"([C]6([H]7)([H]8)([H]9))" +
	"([C]10([H]11)([H]12)([H]13))" +
	".[C.]14([H]15)([H]16)" + # radcial can be anywhere in 2nd fragment
	"[C]17([H]18)([H]19)([H]20)",
	name =
	"dissoziation of a sigma bond for alkans" +
	" 4.8"+
	""
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.09; oder Seite Einband, Alkene
IMS_4_9 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3([C]4)[*+.]5" + #YRY "[C]1[C]2[C]3([C]4)[*+.]5[*]6"
	">>" +
	"[C.]1.[C]2[C]3([C]4){=}[*+.]5", #YRY "[C.]1.[C]2[C]3([C]4){=}[*+.]5[*]6"
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.9" +
	" §R1R3R4Y5" #YRY " §R1R3R4Y5R6"
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.10; oder Seite Einband, Alkene
IMS_4_10 = Rule.fromDFS(
	s =
	"[*+]1[C]2[C.]3" + #YRY "[*+]1[C]2[C]3[C.]4"
	">>" +
	"[*+.]1.[C]2[C.]3", #YRY "[*+.]1[C]2.[C]3[C.]4"
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.10" +
	" §Y1" #YRY " §Y1R2"
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.11; oder Seite Einband, Alkene
IMS_4_11 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3{=}[*+.]4" +
	">>" +
	"[C.]1.[C]2[C]3{#}[*+]4",
	name =
	"radical induced (alpha-)clevage for a unsaturated heteroatom" +
	" 4.11" +
	" §R1R3Y4"
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.12; oder Seite Einband, Alkene
IMS_4_12_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name = 
	"radical induced (alpha-)clevage for a alkene charge left" +
	" 4.12_1" +
	" §R1"
)

IMS_4_12_2 = Rule.fromDFS( 
	s = 
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name =
	"radical induced (alpha-)clevage for a alkene charge right" +
	" 4.12_2" +
	" §R1"
)

# Interpreation von Massenspektren Springer, Seite 60, Gl. 4.13
IMS_4_13_1 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)" +
	"[C]5([H]6)([H]7)" +
	"[O+.]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)" +
	">>" +
	"[C.]1([H]2)([H]3)([H]4)" + 
	".[C]5([H]6)([H]7){=}" +
	"[O+]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.13_1" +
	""
)

IMS_4_13_2 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)" +
	"[C]5([H]6)([H]7)" +
	"[O+.]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)" +
	">>" +
	"[C.]1([H]2)([H]3)([H]4)" + 
	".[C+]5([H]6)([H]7){-}" +
	"[O]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.13_2" +
	""
)

# Interpreation von Massenspektren Springer, Seite 60, Gl. 4.14
IMS_4_14 = Rule.fromDFS(
	s =
	"[C]1" +
	"([C]2[C]3)" +
	"([C]4[C]5)" +
	"{=}[O+.]"
	">>" +
	"[C.]2[C]3" +
	".[C]4[C]5" +
	"[C]1{#}[O+]",
	name =
	"radical induced (alpha-)clevage for a unsaturated heteroatom" +
	" 4.14" +
	""
)

# Interpreation von Massenspektren Springer, Seite 62, Gl. 4.15
IMS_4_15_1_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name =
	"radical induced (alpha-)clevage for a alkene" +
	" 4.15 prod 1 left charge" +
	""
)

IMS_4_15_1_2 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name =
	"radical induced (alpha-)clevage for a alkene" +
	" 4.15 prod 1 right charge" +
	""
)

IMS_4_15_2_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C]1.[C+]2[C]3{=}[C]4",
	name =
	"radical induced (alpha-)clevage for a alkene" +
	" 4.15 prod 2 left charge" +
	""
)

IMS_4_15_2_2 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C+]2[C]3{=}[C]4",
	name =
	"radical induced (alpha-)clevage for a alkene"+
	" 4.15 prod 2 right charge"
	""
)

IMS_4_15_3_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C+.]3[C]4[C]5[C]6[C]7[C]8" +
	">>" +
	"[C]1.[C]2{=}[C+]3[C]4[C]5[C]6[C]7[C]8",
	name =
	"radical induced (alpha-)clevage for a alkene" +
	" 4.15 2nd prod 1" +
	""
)

IMS_4_15_3_2 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C+.]4[C]5[C]6[C]7[C]8" +
	">>" +
	"[C.]1.[C+]2[C]3[C]4[C]5[C]6[C]7[C]8",
	name =
	"radical induced (alpha-)clevage for a alkene" +
	" 4.15 2nd prod 2" +
	""
)

# 4.16 not included as it is a negative example (example cleavage impossible)

# Interpreation von Massenspektren Springer, Seite 63, Gl. 4.17
IMS_4_17 = Rule.fromDFS(
	s =
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]5[C]6" +
	"[C]1" +
	"([C]7)" +
	"[O+.]8",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.17" +
	""
)

IMS_4_17_1 = Rule.fromDFS(
	s =
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]5[C]6" +
	"[C]1" +
	"([C]7)" +
	"[O+.]8" +
	".[C]2[C]3[C]4",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.17_1" +
	""
)

IMS_4_17_2 = Rule.fromDFS(
	s =
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]2[C]3[C]4" +
	"[C]1" +
	"([C]7)" +
	"[O+.]8" +
	".[C]5[C]6",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.17_2" +
	""
)

IMS_4_17_3 = Rule.fromDFS(
	s =
	"[C]1" +
	"([C]2[C]3[C]4)" +
	"([C]5[C]6)" +
	"([C]7)" +
	"([O+.]8)" +
	">>" +
	"[C]2[C]3[C]4" +
	"[C]1" +
	"([C]5[C]6)" +
	"[O+.]8" +
	".[C]7", 
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" 4.17_3" +
	""
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.18; Seite Einband
IMS_4_18 = Rule.fromDFS(
	s =
	"[*]1[*+.]2" + #YRY "[C]1[*+.]2[C]3"
	">>" +
	"[*+]1.[*.]2", #YRY "[C+]1.[*.]2[C]3"
	name =
	"inductive cleavage odd electron 1" +
	" 4.18"
	" §R1Y2" #YRY " §R1Y2R3"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 with Information of 4.25 of R'
IMS_4_19_1 = Rule.fromDFS(
	s =
	"[*]1([C]2)[*]3{=}[*+.]4" +
	">>" +
	"[*+]1.[C]2[*.]3{=}[*]4", 
	name =
	"inductive cleavage odd electron 2" +
	" 4.19"
	" §R1R3Y4"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 2te Variante
IMS_4_19_2 = Rule.fromDFS(# Y on left side has unpaired electron
	s =
	"[*]1([*]3)[C+]4{=}[*.]2" +
	">>" +
	"[*+]1.[*]3[C.]4{=}[*]2", 
	name =
	"inductive cleavage odd electron 3" +
	" 4.19" +
	" §R1R3Y2"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.20
IMS_4_20 = Rule.fromDFS(
	s =
	"[*]1[*+]2[H]3([H]4)" +
	">>" +
	"[*+]1.[*]2[H]3([H]4)",
	name =
	"inductive cleavage even electron 1" +
	" 4.20" +
	" §R1Y2"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.21
IMS_4_21 = Rule.fromDFS(
	s =
	"[*]1[*+]2{=}[C]3[H]4([H]5)" +
	">>" +
	"[*+]1.[*]2{=}[C]3[H]4([H]5)",
	name =
	"inductive cleavage even electron 2" +
	" 4.21" +
	" §R1Y2"
)

# Interpreation von Massenspektren Springer, Seite 67, Gl. 4.22
IMS_4_22 = Rule.fromDFS(
	s =
	"[C]1[C]2" +
	"[*+.]3" +
	"[C]4[C]5" +
	">>" +
	"[C+]1[C]2" +
	"[*.]3" +
	"[C]4[C]5",
	name =
	"inductive cleavage odd electron" +
	" 4.22" +
	""
)

# Interpreation von Massenspektren Springer, Seite 67, Gl. 4.23
IMS_4_23_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1[C]2[C]3[C]4.[H]5[Cl+.]6",
	name =
	"inductive cleavage odd electron" +
	" 4.23 prod 1" +
	""
)

IMS_4_23_2 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1[C]2[C]3.[C]4[H]5[Cl+.]6",
	name =
	"inductive cleavage odd electron" +
	" 4.23 prod 1" +
	""
)

# Interpreation von Massenspektren Springer, Seite 67, Gl. 4.24
IMS_4_24_1 = Rule.fromDFS(
	s =
	"[C]1([C]2)([C]3)[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1[C]2[C]3[C]4.[H]5[Cl+.]6",
	name =
	"inductive cleavage odd electron" +
	" 4.24 prod 1" +
	""
)

IMS_4_24_2 = Rule.fromDFS(
	s =
	"[C]1([C]2)([C]3)[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1([C]2)([C]3).[C]4[H]5[Cl+.]6",
	name =
	"inductive cleavage odd electron" +
	" 4.24 prod 1" +
	""
)

# Interpreation von Massenspektren Springer, Seite 67, Gl. 4.25
IMS_4_25_1 = Rule.fromDFS(
	s =
	"[C]1[C]2([C]3){=}[O+.]4" +
	">>" +
	"[C+]1.[C]3[C.]2{=}[O]4",
	name =
	"inductive cleavage odd electron" +
	" 4.25 reactant 1" +
	" §R1R3"
)

IMS_4_25_2 = Rule.fromDFS(
	s =
	"[*]1[C+]2([*]3)[O.]4" +
	">>" +
	"[*+]1.[*]3[C.]2{=}[O]4",
	name =
	"inductive cleavage odd electron" +
	" 4.25 reactant 2" +
	" §R1R3"
)

# Interpreation von Massenspektren Springer, Seite 68, Gl. 4.26
IMS_4_26_1 = Rule.fromDFS(
	s =
	"[*]1[C]2([H]3)([H]4)[O+.]5[*]6" +
	">>" +
	"[*.]1.[C]2([H]3)([H]4){=}[O+]5[*]6",
	name =
	"inductive cleavage even electron" +
	" 4.26 step 1 alpha" +
	" §R1R6"
)

IMS_4_26_2 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3){=}[O+]4[*]5" +
	">>" +
	"[C]1([H]2)([H]3)[O]4.[*+]5",
	name =
	"inductive cleavage even electron" +
	" 4.26 step 2 inductive" +
	" §R5"
)

# Interpreation von Massenspektren Springer, Seite 68, Gl. 4.27
IMS_4_27_1 = Rule.fromDFS(
	s =
	"[*]1[C]2([*]3){=}[O+.]4" +
	">>" +
	"[*]1.[*]3[C]2{#}[O+]4",
	name =
	"inductive cleavage even electron" +
	" 4.27 step 1 alpha" +
	" §R1R3"
)

IMS_4_27_2 = Rule.fromDFS(
	s =
	"[*]1[C]2{#}[O+]3" +
	">>" +
	"[*+]1.[C]2[O]3",
	name =
	"inductive cleavage even electron" +
	" 4.27 step 2 inductive" +
	" §R1"
)

# Interpreation von Massenspektren Springer, Seite 68, Gl. 4.28
IMS_4_28_1 = Rule.fromDFS(
	s =
	"[*]1[O]2[H]3.[H+]4" +
	">>" +
	"[*]1[O+]2([H]3)([H]4)",
	name =
	"inductive cleavage even electron" +
	" 4.28 step 1 chemical ionization" +
	" §R1"
)

IMS_4_28_2 = Rule.fromDFS(
	s =
	"[*]1[O+]2([H]3)([H]4)" +
	">>" +
	"[*+]1.[O]2([H]3)([H]4)",
	name =
	"inductive cleavage even electron" +
	" 4.28 step 2 inductive" +
	" §R1"
)

# Interpreation von Massenspektren Springer, Seite 70, Gl. 4.29
IMS_4_29 = Rule.fromDFS(
	s =
	"[*]1[C]2[C]3[C]4[C]5[C]6" +
	"[C]7([H]8)[O]9([H]10)" +
	"[C]11([H]12)[C]13([H]14)([H]15)([H]16)" +
	"[N+]17([H]18)([H]19)[C]20([H]21)([H]22)([H]23)" +
	">>" +
	"[*]1[C]2[C]3[C]4[C]5[C]6" +
	"[C]7([H]8)[O]9([H]10)" +
	"[C+]11([H]12)[C]13([H]14)([H]15)([H]16)" +
	".[N]17([H]18)([H]19)[C]20([H]21)([H]22)([H]23)",
	name =
	"inductive cleavage even electron" +
	" 4.29" +
	" §R1"
)


# Interpreation von Massenspektren Springer, Seite 71, Gl. 4.30
IMS_4_30 = Rule.fromDFS(
    s =
	"[C.]1[C]2[C]3[C+]4[C]5{=}[C]6" +
	">>" +
	"[C.]1[C+]2.[C]3{=}[C]4[C]5{=}[C]6",
	name =
    "Ring spaltung generell" +
	" 4.30" +
	""
)

# Interpreation von Massenspektren Springer, Seite 72, Gl. 4.31
IMS_4_31_alpha1 = Rule.fromDFS(
    s =
	"[C]1[C]2[C]3[C]4[C+]5[C.]6[C]7{-}2" +
	">>" +
	"[C]1[C.]2[C]3[C]4[C+]5[C]6{=}[C]7",
	name =
    "retro diels alder charge conservation" +
    " 4.31 alpha 1" +
    " §R1"
)

IMS_4_31_alpha2 = Rule.fromDFS(
    s =
	"[C]1[C.]2[C]3[C]4[C+]5[C]6{=}[C]7" +
	">>" +
	"[C]1[C]2{=}[C]3.[C.]4[C+]5[C]6{=}[C]7",
	name =
    "retro diels alder charge conservation" +
    " 4.31 alpha 2" +
    " §R1"
)

# Interpreation von Massenspektren Springer, Seite 72, Gl. 4.32
IMS_4_32_alpha = Rule.fromDFS( #equivalten to 4.31 alpha1
    s =
	"[C]1[C]2[C]3[C]4[C+]5[C.]6[C]7{-}2" +
	">>" +
	"[C]1[C.]2[C]3[C]4[C+]5[C]6{=}[C]7",
	name =
    "retro diels alder charge drift" +
    " 4.32 alpha" +
    " §R1"
)

IMS_4_32_ind = Rule.fromDFS(
    s =
	"[C]1[C.]2[C]3[C]4[C+]5[C]6{=}[C]7" +
	">>" +
	"[C]1[C.]2[C+]3.[C]4{=}[C]5[C]6{=}[C]7",
	name =
    "retro diels alder charge drift" +
    " 4.32 ind" +
    " §R1"
)

# Interpreation von Massenspektren Springer, Seite 74, Gl. 4.33
IMS_4_33_rH = Rule.fromDFS(
	s =
	"[C]1[C]2([H]3)[C]4[C]5[C]6([C]7){=}[O+.]8" +
	">>" +
	"[C]1[C.]2[C]4[C]5[C]6([C]7){=}[O+]8[H]3",
	name=
    "gamma H-migr. to unsat. group with beta cleavage" + 
    " 4.33 rH" +
	" §R1"
)

IMS_4_33_alpha_1 = Rule.fromDFS(
	s =
	"[C]1[C.]2[C]3[C]4[C]5([C]6){=}[O+]7[H]8" +
	">>" +
	"[C]1[C]2{=}[C]3.[C.]4[C]5([C]6){=}[O+]7[H]8",
	name=
    "gamma H-migr. to unsat. group with beta cleavage" + 
    " 4.33 alpha 1" +
	" §R1"
)

IMS_4_33_alpha_2 = Rule.fromDFS(
	s =
	"[C]1[C.]2[C]3[C]4[C]5([C]6){=}[O+]7[H]8" +
	">>" +
	"[C]1[C]2{=}[C]3.[C.]4{=}[C]5([C]6)[O+.]7[H]8",
	name=
    "gamma H-migr. to unsat. group with beta cleavage" + 
    " 4.33 alpha 2" +
	" §R1"
)

# Interpreation von Massenspektren Springer, Seite 74, Gl. 4.34
IMS_4_34_rH = Rule.fromDFS(
	s =
	"[C]1[C]2([H]3)[C]4[C]5[C]6([C]7){=}[O+.]8" +
	">>" +
	"[C]1[C.]2[C]4[C]5[C+]6([C]7)[O]8[H]3",
	name=
    "gamma H-migr. to unsat. group with beta cleavage" + 
    " 4.34 rH" +
	" §R1"
)

IMS_4_34_ind = Rule.fromDFS(
	s =
	"[C]1[C.]2[C]3[C]4[C+]5([C]6)[O]7[H]8" +
	">>" +
	"[C]1[C.]2[C+]3.[C]4{=}[C]5([C]6)[O]7[H]8",
	name=
    "gamma H-migr. to unsat. group with beta cleavage" +
    " 4.34 inductive" +
	" §R1"
)

# Interpreation von Massenspektren Springer, Seite 75, Gl. 4.35
IMS_4_35_rHalpha = Rule.fromDFS(
	s =
	"[C]1[C]2([H]3)[C]4[C]5[C]6{=}[N+.]8[N]9([C]10)[C]11" +
	">>" +
	"[C]1[C]2{=}[C]4.[C.]5[C]6{=}[N+]8([H]3)[N]9([C]10)[C]11",
	name=
    "gamma H-migr. to unsaturated group Odd electron Ion" +
    " 4.35 rH alpha" +
	""
)

# Interpreation von Massenspektren Springer, Seite 75, Gl. 4.36
IMS_4_36_ = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C]7{=}[C]8[C]9{=}[C]10[C]11{=}[C]12{-}7" + # ring has somewhere +.
	">>" +
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C+]7[C.]8[C]9{=}[C]10[C]11{=}[C]12{-}7",
	name=
    "gamma H-migr. to unsaturated group Odd electron Ion" + 
    " 4.36 charge move" +
	""
)

IMS_4_36__rHalpha = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3([H]4)[C]5[C]6[C+]7[C.]8[C]9{=}[C]10[C]11{=}[C]12{-}7" +
	">>" +
	"[C]1[C]2[C]3{=}[C]5.[C.]6[C+]7[C]8([H]4)[C]9{=}[C]10[C]11{=}[C]12{-}7",
	name=
    "gamma H-migr. to unsaturated group Odd electron Ion" + 
    " 4.36 rH alpha" +
	""
)

# Interpreation von Massenspektren Springer, Seite 78, Gl. 4.37
IMS_4_37_rH = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3([H]4)[C]5[C]6[C]7[O+.]8[H]9" +
    ">>" +
    "[C]1[C]2[C.]3[C]5[C]6[C]7[O+]8([H]4)[H]9",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.37 rH" +
    ""
)

IMS_4_37_rd = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6[O+]7([H]8)[H]9" +
    ">>" +
    "[C]1[C]2[C]3[C]4[C]5[C]6{-}3.[O+.]7([H]8)[H]9",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.37 rd" +
    ""
)

# Interpreation von Massenspektren Springer, Seite 78, Gl. 4.38
IMS_4_38_rH = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3([H]4)[C]5[C]6[C]7[O+.]8[H]9" +
    ">>" +
    "[C]1[C]2[C.]3[C]5[C]6[C]7[O+]8([H]4)[H]9",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.38 rH" +
    ""
)

IMS_4_38_ind = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6[O+]7([H]8)[H]9" +
    ">>" +
    "[C]1[C]2[C.]3[C]4[C]5[C+]6.[O]7([H]8)[H]9",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.38 ind" +
    ""
)

IMS_4_38_ind_2 = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C+]6" +
    ">>" +
    "[C]1[C]2[C.]3[C+]4.[C]5{=}[C]6",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.38 ind" +
    ""
)

# Interpreation von Massenspektren Springer, Seite 79, Gl. 4.39
IMS_4_39_rH = Rule.fromDFS(
    s =
    "[C]1([H]2)[C]3({=}[O]4)[N+.]5([H]6)[C]7[C]8[C]9[C]10" +
    ">>" +
    "[C.]1[C]3({=}[O]4)[N+]5([H]2)([H]6)[C]7[C]8[C]9[C]10",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.39 rH" +
    ""
)

IMS_4_39_alpha = Rule.fromDFS(
    s =
    "[C.]1[C]2({=}[O]3)[N+]4([H]5)([H]6)[C]7[C]8[C]9[C]10" +
    ">>" +
    "[C]1{=}[C]2{=}[O]3.[N+.]4([H]5)([H]6)[C]7[C]8[C]9[C]10",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.39 alpha" +
    ""
)

# Interpreation von Massenspektren Springer, Seite 79, Gl. 4.40
IMS_4_40_rH = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3([H]4)[C]5[C]6[Cl+.]7" +
    ">>" +
    "[C]1[C]2[C.]3[C]5[C]6[Cl+]7[H]4",
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.40 rH" +
    ""
)

IMS_4_40_ind = Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[Cl+]6[H]7" +
    ">>" +
    "[C]1[C]2[C]3[C]4[C+.]5{-}3.[Cl]6[H]7", # charge somewhere in cycle
    name =
    "H-migration to unsat. hetroatom and clevage of neighb. bond" +
    " 4.40 ind" +
    ""
)

# Interpreation von Massenspektren Springer, Seite 80, Gl. 4.41
IMS_4_41_rH = Rule.fromDFS(
    s =
    "[H]1[*]2[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8({=}3)[C]9({=}[O]10)[O+.]11[C]12" +
    ">>" +
    "[*.]2[C]3[C]4{=}[C]5[C]6{=}[C]7[C]8({=}3)[C]9({=}[O]10)[O+]11([H]1)[C]12",
    name =
    "H-migr to unsat. hetrostructur and clevage of neighb. bond" +
    " 4.41 rH" +
    " §Y2R12"
)

IMS_4_41_ind1 = Rule.fromDFS(
    s =
    "[*.]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({=}2)[C]8({=}[O]9)[O+]10([H]11)[C]12" +
    ">>" +
    "[*.]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({=}2)[C]8{#}[O+]9.[O]10([H]11)[C]12",
    name =
    "H-migr to unsat. hetrostructur  and clevage of neighb. bond" +
    " 4.41 ind prod 1" +
    " §Y1R12"
)

IMS_4_41_ind2 = Rule.fromDFS(
    s =
    "[*.]1[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({=}2)[C]8({=}[O]9)[O+]10([H]11)[C]12" +
    ">>" +
    "[*]1{=}[C]2[C]3{=}[C]4[C]5{=}[C]6[C]7({-}2){=}[C]8{=}[O+]9.[O]10([H]11)[C]12",
    name =
    "H-migr to unsat. hetrostructur  and clevage of neighb. bond" +
    " 4.41 ind prod 2" +
    " §Y1R12"
)

# Interpreation von Massenspektren Springer, Seite 81, Gl. 4.42
IMS_4_42_rd = Rule.fromDFS(
    s =
    "[C]1[C]2[C]3[C]4[C]5[Cl+.]6" +
    ">>" +
    "[C.]1.[C]2[C]3[C]4[C]5[Cl+]6{-}2",
    name =
    "displacement reaction" +
    " 4.42 rd" +
    " §R1"
)

# Interpreation von Massenspektren Springer, Seite 82, Gl. 4.43
IMS_4_43_ = Rule.fromDFS(
    s =
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)" +
	"[N+.]8([H]9)[C]10([H]11)([H]12)[C]13([H]14)([H]15)[H]16" +
    ">>" +
	"[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)" +
	"[N+]8([H]9){=}[C]10([H]11)([H]12).[C.]13([H]14)([H]15)[H]16",
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

# Interpreation von Massenspektren Springer, Seite 82, Gl. 4.44
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

# Interpreation von Massenspektren Springer, Seite 84, Gl. 4.45
IMS_4_45_rH = Rule.fromDFS(
    s =
    "[C]1[C]2([H]3)[C]4[O]5[C]6([C]7){=}[O+.]8" +
    ">>" +
    "[C]1[C.]2[C]4[O]5[C]6([C]7){=}[O+]8[H]3",
    name =
    "displacement reaction" +
    " 4.45 rH" +
    " §R1R7"
)

IMS_4_45_alpha = Rule.fromDFS(
    s =
    "[C]1[C.]2[C]3[O]4[C]5([C]6){=}[O+]7[H]8" +
    ">>" +
    "[C]1[C]2[C]3.[O+.]4{=}[C]5([C]6)[O+]7[H]8",
    name =
    "displacement reaction" +
    " 4.45 alpha" +
    " §R1R6"
)

# Interpreation von Massenspektren Springer, Seite 84, Gl. 4.46
IMS_4_46_rH_1 = Rule.fromDFS(
    s =
    "[H]1[C]2[C]3([H]4)[C]5[O]6[C]7([C]8){=}[O+.]9" +
    ">>" +
    "[H]1[C]2[C.]3[C]5[O+]6[C]7([C]8){=}[O]9[H]4",
    name =
    "displacement reaction" +
    " 4.46 rH" +
    " §R2R8"
)

IMS_4_46_rH_2 = Rule.fromDFS(
    s =
    "[H]1[C]2[C.]3[C]4[O]5[C]6([C]7){=}[O]8[H]9" +
    ">>" +
    "[C]2[C.]3[C]4.[H]1[O+]5{=}[C]6([C]7)[O]8[H]9", # radical anywhere on first fragment
    name =
    "displacement reaction" +
    " 4.46 rH2 var 1" +
    " §R2R7"
)

IMS_4_46_rH_2_ = Rule.fromDFS(
    s =
    "[H]1[C]2[C.]3[C]4[O]5[C]6([C]7){=}[O]8[H]9" +
    ">>" +
    "[C]2[C.]3[C]4.[H]1[O+]5[C]6([C]7){=}[O+]8[H]9", # radical anywhere on first fragment
    name =
    "displacement reaction" +
    " 4.46 rH2 var 2" +
    " §R2R7"
)


IMS_examples = [
    IMS_4_3_var1,
    IMS_4_3_var2,

	IMS_4_7,
    IMS_4_8,
	IMS_4_9,
	IMS_4_9,
	IMS_4_10,
	IMS_4_11,
	IMS_4_12_1,
	IMS_4_12_2,
	IMS_4_13_1,
	IMS_4_13_2,
	IMS_4_14,
	IMS_4_15_1_1,
	IMS_4_15_1_2,
	IMS_4_15_2_1,
	IMS_4_15_2_2,
	IMS_4_15_3_1,
	IMS_4_15_3_2,
	# 4.16 negative example
	IMS_4_17_1,
	IMS_4_17_2,
	IMS_4_17_3,
    IMS_4_18,
	IMS_4_19_1,
	IMS_4_19_2,
	IMS_4_20,
	IMS_4_21,
	IMS_4_22,
	IMS_4_23_1,
	IMS_4_23_2,
	IMS_4_24_1,
	IMS_4_24_2,
	IMS_4_25_1,
	IMS_4_25_2,
	IMS_4_26_1,
	IMS_4_26_2,
	IMS_4_27_1,
	IMS_4_27_2,
	IMS_4_28_1,
	IMS_4_28_2,
	IMS_4_29,
    IMS_4_30,
    IMS_4_31_alpha1,
    IMS_4_31_alpha2,
    IMS_4_32_alpha,
    IMS_4_32_ind,
    IMS_4_33_rH,
    IMS_4_33_alpha_1,
    IMS_4_33_alpha_2,
    IMS_4_34_rH,
    IMS_4_34_ind,
    IMS_4_35_rHalpha,
    IMS_4_36_,
    IMS_4_36__rHalpha,
    IMS_4_37_rH,
    IMS_4_37_rd,
    IMS_4_38_rH,
    IMS_4_38_ind,
    IMS_4_38_ind_2,
    IMS_4_39_rH,
    IMS_4_39_alpha,
    IMS_4_40_rH,
    IMS_4_40_ind,
    IMS_4_41_rH,
    IMS_4_41_ind1,
    IMS_4_41_ind2,
    IMS_4_42_rd,
    IMS_4_43_,
    IMS_4_43_rH,
    IMS_4_44_ind,
    IMS_4_44_rH,
    IMS_4_45_rH,
    IMS_4_45_alpha,
    IMS_4_46_rH_1,
    IMS_4_46_rH_2,
    IMS_4_46_rH_2_,
]
