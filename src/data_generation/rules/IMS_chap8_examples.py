import mod

# Interpreation von Massenspektren Springer, Seite 143, Gl. 8.1
IMS_8_1_var1_step1 = mod.Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)"
    "[C]8([H]9)([H]10)[C]11([H]12){=}[C+.]13([H]14)([H]15)"
    ">>"
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)"
    "[C]8([H]9){=}[C]11([H]12)[C+.]13([H]14)([H]15)([H]10)",
    name =
    "monomolecular ion-cleavage"
	" 8.1 rH -0.6"
	""
)

IMS_8_1_var1_step2 = mod.Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)"
    "[C]5([H]6)([H]7)[C]8([H]9){=}[C]10([H]11)[C+.]12([H]13)([H]14)([H]15)"
    ">>"
    "[H]1[C.]2([H]3)([H]4)"
    "."
    "[C]5([H]6){=}[C]8([H]9)[C+]10([H]11)([H]7)[C]12([H]13)([H]14)([H]15)",
    name =
    "monomolecular ion-cleavage"
	" 8.1 alpha 1.0"
	""
)

IMS_8_1_var1_step3 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2){=}[C]3([H]4)[C+]5([H]6)([H]7)"
    "[C]8([H]9)([H]10)([H]11)"
    ">>"
    "[C]1([H]2):[C+]3([H]4):[C]5([H]6):1"
    "."
    "[H]7[C]8([H]9)([H]10)([H]11)", # aromatic cyclopropenium (e(ar) ring); https://en.wikipedia.org/wiki/Cyclopropenium_ion
    name =
    "monomolecular ion-cleavage"
	" 8.1 rH 2.5"
	""
)

IMS_8_1_var2_step1 = mod.Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)"
    "[C]11([H]12){=}[C+.]13([H]14)([H]15)"
    ">>"
    "[H]1[C]2([H]3)([H]4)[C.]5([H]6)([H]7).[C+]8([H]9)([H]10)"
    "[C]11([H]12){=}[C]13([H]14)([H]15)",
    name =
    "monomolecular ion-cleavage"
	" 8.1 alpha 1.7"
	""
)

IMS_8_1_var2_step2 = mod.Rule.fromDFS(
    s =
    "[C+]1([H]2)([H]3)[C]4([H]5){=}[C]6([H]7)([H]8)"
    ">>"
    "[C+]1([H]2):[C]4([H]5):[C]6([H]7):1" # aromatic cyclopropenium (e(ar) ring); charge delocalised over ring; https://en.wikipedia.org/wiki/Cyclopropenium_ion
    "."
    "[H]3[H]8",
    name =
    "monomolecular ion-cleavage"
	" 8.1 rH 3.0"
	""
)

IMS_8_1_var3_step1 = mod.Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)"
    "([H]10)[C]11([H]12){=}[C+.]13([H]14)([H]15)"
    ">>"
    "[C.]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)"
    "([H]10)[C+]11([H]12)[C]13([H]14)([H]15)([H]1)",
    name =
    "monomolecular ion-cleavage"
	" 8.1 rH 0.3"
	""
)

IMS_8_1_var3_step2 = mod.Rule.fromDFS(
    s =
    "[C.]1([H]2)([H]3)[C]4([H]5)([H]6)"
    "[C]7([H]8)([H]9)[C+]10([H]11)[C]12([H]13)([H]14)([H]15)"
    ">>"
    "[C]1([H]2)([H]3)[C]4([H]5)([H]6)"
    "."
    "[C]7([H]8)([H]9)([H]11)[C]10([H]13){=}[C+.]12([H]14)([H]15)",
    name =
    "monomolecular ion-cleavage"
	" 8.1 alpha 1.1"
	""
)

# Interpreation von Massenspektren Springer, Seite 144, Gl. 8.2
IMS_8_2_bidirectional_down = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)"
    "([H]13)[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]8([H]9)([H]10)[C]11([H]12)"
    "([H]13)[C]14([C]15([H]16)([H]17)([H]18)){=}[O+]19([H]7)",
    name =
    "monomolecular ion-cleavage"
	" 8.2 bidirectional down"
	""
)

IMS_8_2_bidirectional_up = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]7([H]8)([H]9)"
    "[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+]18([H]19)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]19)[C]7([H]8)([H]9)"
    "[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+.]18",
    name =
    "monomolecular ion-cleavage"
	" 8.2 bidirectional up"
	""
)

# 1st line
IMS_8_2_alpha_1_1 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)"
    "[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C.]11([H]12)([H]13)"
    "."
    "[C]15([H]16)([H]17)([H]18)[C]14{#}[O+]19",
    name =
    "monomolecular ion-cleavage"
	" 8.2 alpha 1.1"
	""
)

IMS_8_2_ind_4_5 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5{#}[O+]6"
    ">>"
    "[C+]1([H]2)([H]3)([H]4)"
    "."
    "[C]5{=}[O]6",
    name =
    "monomolecular ion-cleavage"
	" 8.2 inductive 4.5"
	""
)

# 2nd line
IMS_8_2_ind_2_1 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)"
    "[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+]11([H]12)([H]13)"
    "."
    "[C]15([H]16)([H]17)([H]18)[C.]14{=}[O]19",
    name =
    "monomolecular ion-cleavage"
	" 8.2 inductive 2.1"
	""
)

IMS_8_2_ind_3_1 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[C]8([H]9)([H]10)[C+]11([H]12)([H]13)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C+]5([H]6)([H]7)"
    "."
    "[C]8([H]9)([H]10)[C]11([H]12)([H]13)",
    name =
    "monomolecular ion-cleavage"
	" 8.2 inductive 3.1"
	""
)

# 3rd line
IMS_8_2_alpha_0_7 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[C]8([H]9)([H]10)[C]11([H]12)([H]13)"
    "[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14[O+]19"
    "."
    "[C.]15([H]16)([H]17)([H]18)",
    name =
    "monomolecular ion-cleavage"
	" 8.2 alpha 0.7"
	""
)

IMS_8_2_ind_2_7 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[C]8([H]9)([H]10)[C+]11([H]12)([H]13)[C]14[O+]15"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[C]8([H]9)([H]10)[C+]11([H]12)([H]13)"
     "."
     "[C]14[O]15",
    name =
    "monomolecular ion-cleavage"
	" 8.2 inductive 2.7"
	""
)

# 4th line
IMS_8_2_alpha_0_6 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]7([H]8)([H]9)"
    "[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+]18([H]19)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6){=}[C]7([H]8)([H]9)"
    "."
    "[C]10([H]11)([H]12){=}[C]13([C]14([H]15)([H]16)([H]17)){=}[O+.]18([H]19)",
    name =
    "monomolecular ion-cleavage"
	" 8.2 alpha 0.6"
	""
)

IMS_8_2_rH_2_0 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3){=}[C]4([C]5([H]6)([H]7)([H]8)){=}[O+.]9([H]10)"
    ">>"
    "[C.]1([H]2)([H]3)([H]10)"
    "."
    "[C]4([C]5([H]6)([H]7)([H]8))[O+]9",
    name =
    "monomolecular ion-cleavage"
	" 8.2 rH 2.0"
	""
)

# 5th line
IMS_8_2_ind_1_6 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]7([H]8)([H]9)"
    "[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+]18([H]19)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C+.]5([H]6)[C]7([H]8)([H]9)"
    "."
    "[C]10([H]11)([H]12){=}[C]13([C]14([H]15)([H]16)([H]17))[O]18([H]19)",
    name =
    "monomolecular ion-cleavage"
	" 8.2 inductive 1.6"
	""
)

IMS_8_2_alpha_3_8 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C+.]5([H]6)[C]7([H]8)([H]9)"
    ">>"
    "[C]1([H]2)([H]3)[C+]5([H]6)[C]7([H]8)([H]9)" "." "[H.]4",
    name =
    "monomolecular ion-cleavage"
	" 8.2 alpha 3.8"
	""
)

# Interpreation von Massenspektren Springer, Seite 147, Gl. 8.3
IMS_8_3_ind = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)"
    "[C+.]11([H]12)([H]13)"
    "[O]14[C]15([H]16)([H]17)([H]18)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)"
    "[C+]11([H]12)([H]13)"
    "."
    "[O+]14[C]15([H]16)([H]17)([H]18)",
    name =
    "monomolecular ion-cleavage"
	" 8.3 ind"
	""
)

IMS_8_3_alpha = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+.]8([H]9)([H]10)"
    "[C]11([H]12)([H]13)[O]14[C]15([H]16)([H]17)([H]18)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+]8([H]9)([H]10)"
    "."
    "[C]11([H]12)([H]13){=}[O+]14[C]15([H]16)([H]17)([H]18)",
    name =
    "monomolecular ion-cleavage"
	" 8.3 alpha"
	""
)

# Interpreation von Massenspektren Springer, Seite 147, Gl. 8.4
IMS_8_4 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)"
    "[C+.]11([H]12)([H]13)[C]14[O]15[C]16([H]17)([H]18)([H]19)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)"
    "[C+.]11([H]12)([H]13)"
    "."
    "[C]16([H]17)([H]18)([H]19)[C]14[O+]15",
    name =
    "monomolecular ion-cleavage"
	" 8.4 ind"
	""
)

# Interpreation von Massenspektren Springer, Seite 148, Gl. 8.5
IMS_8_5_1 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)"
    "[C]14([H]15)([H]16)[C]17([H]18)([H]19){=}[O+.]20"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+.]8([H]9){=}[C]11([H]12)([H]13)" "."
    "[C]14([H]15)([H]16){=}[C]17([H]18)([H]19)[O+.]20[H]10",
    name =
    "monomolecular ion-cleavage"
	" 8.5 row 1"
	""
)

IMS_8_5_2 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)"
    "[O]14([H]15)([H]16)[C]17([H]18)([H]19){=}[C+.]20([H]21)([H]22)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+.]8([H]9){=}[C]11([H]12)([H]13)"
    "."
    "[O+.]14([H]15)([H]16){=}[C]17([H]18)([H]19)[C]20([H]21)([H]22)([H]10)",
    name =
    "monomolecular ion-cleavage"
	" 8.5 row 2"
	""
)

# Interpreation von Massenspektren Springer, Seite 149, Gl. 8.6
IMS_8_6_1 = mod.Rule.fromDFS(
    s =
    "[C]1[C]2{=}[C]3[C]4[C]5[C+.]6([C]7{=}[C]8){-}1"
    ">>"
    "[C]1[C+]2[C]3[C]4[C]5[C]6[C.]7[C]8",
    name =
    "stepwise symetric openchained intermediate product"
    " 8.6 var 1"
    ""
)

IMS_8_6_2 = mod.Rule.fromDFS(
    s =
    "[C]1[C]2{=}[C]3[C]4[C]5[C+.]6([C]7{=}[C]8){-}1"
    ">>"
    "[C]1[C.]2[C]3[C]4[C]5[C]6[C+]7[C]8",
    name =
    "stepwise symetric openchained intermediate product"
    " 8.6 var 2"
    ""
)

IMS_8_6_3 = mod.Rule.fromDFS(
    s =
    "[C]1[C+]2[C]3[C]4[C]5[C]6[C.]7[C]8"
    ">>"
    "[C]1{=}[C+]2[C]3{=}[C]4.[C]5{=}[C]6[C.]7{=}[C]8",
    name =
    "stepwise symetric openchained intermediate product"
    " 8.6 var 1 alpha"
    ""
)

IMS_8_6_4 = mod.Rule.fromDFS(
    s =
    "[C]1[C.]2[C]3[C]4[C]5[C]6[C+]7[C]8"
    ">>"
    "[C]1{=}[C.]2[C]3{=}[C]4" "." "[C]5{=}[C]6[C+]7{=}[C]8",
    name =
    "stepwise symetric openchained intermediate product"
    " 8.6 var 2 alpha"
    ""
)

# Interpreation von Massenspektren Springer, Seite 150, Gl. 8.7
IMS_8_7_1 = mod.Rule.fromDFS(
    s =
    "[C]1[C]2[C]3([H]4)[C]5[C]6[C]7([H]8){=}[O+.]9"
    ">>"
    "[C]1[C]2[C.]3[C]5[C]6[C]7([H]8){=}[O+]9[H]4",
    name =
    "Hydrogen exchange occring in a Ion-Molecule-Complex"
    " 8.7 row 1 rH"
    ""
)

IMS_8_7_2 = mod.Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6([H]7){=}[O+]8[H]9"
    ">>"
    "[C]1[C]2[C]3{=}[C]4"
    "."
    "[C]5{=}[C]6([H]7)[O+.]8[H]9",
    name =
    "Hydrogen exchange occring in a Ion-Molecule-Complex"
    " 8.7 row 1 high energy"
    ""
)

# intermediate step, jumping over
IMS_8_7_3 = mod.Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6([H]7){=}[O+]8[H]9"
    ">>"
    "[C]1[C]2[C]3{=}[C]4"
    "."
    "[C]5{=}[C]6([H]7)[O+.]8[H]9", #H7 disapears in original
    name =
    "Hydrogen exchange occring in a Ion-Molecule-Complex"
    " 8.7 row 2 low energy"
    ""
)

# intermediate step, jumping over
IMS_8_7_4 = mod.Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6([H]7){=}[O+]8[H]9" # starting in row 1
    ">>"
    "[C]1[C]2([H]9)[C+]3[C]4[H]7" # product in row 3
    "."
    "[C]5{=}[C]6[O.]8",
    name =
    "Hydrogen exchange occring in a Ion-Molecule-Complex"
    " 8.7 row 3 process 1"
    ""
)

# final product
IMS_8_7_5 = mod.Rule.fromDFS(
    s =
    "[C]1[C]2[C.]3[C]4[C]5[C]6([H]7){=}[O+]8[H]9"
    ">>"
    "[C]1[C]2{=}[C+.]3[C]4"
    "."
    "[H]7[C]5[C]6([H]9){=}[O]8",
    name =
    "Hydrogen exchange occring in a Ion-Molecule-Complex"
    " 8.7 row 3 process 2"
    ""
)

# Interpreation von Massenspektren Springer, Seite 151, Gl. 8.8
IMS_8_8_1 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)[O+.]7[C]8([H]9)([H]10){-}5"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6){=}[O+]7[C.]8([H]9)([H]10)",
    name =
    "rearangement with stable Acylium-Ion"
    " 8.8 row 1 process 1"
    ""
)

IMS_8_8_2 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6){=}[O+]7[C.]8([H]9)([H]10)"
    ">>"
    "[C]1([H]2)([H]3){=}[C]5([H]6)[O+.]7[C]8([H]9)([H]10)([H]4)",
    name =
    "rearangement with stable Acylium-Ion"
    " 8.8 row 1 process 2"
    ""
)

IMS_8_8_2b = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3){=}[C]4([H]5)[O+.]6[C]7([H]8)([H]9)([H]10)"
    ">>"
    "[C]1([H]2)([H]3)([H]10)[C]4([H]5){=}[O+]6[C.]7([H]8)([H]9)",
    name =
    "rearangement with stable Acylium-Ion"
    " 8.8 row 1 process 2 back"
    ""
)

IMS_8_8_3 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3){=}[C]4([H]5)[O+.]6[C]7([H]8)([H]9)([H]10)"
    ">>"
    "[C]1([H]2)([H]3)([H]5)[C]4{#}[O+]6"
    "."
    "[C.]7([H]8)([H]9)([H]10)",
    name =
    "rearangement with stable Acylium-Ion"
    " 8.8 row 2 process 2"
    ""
)

# Interpreation von Massenspektren Springer, Seite 152, Gl. 8.9
IMS_8_9_1_CH3 = mod.Rule.fromDFS(
    s =
    "[_A]1[C]2[C]3([H]4)[C]5{=}[C]6[C]7([C]8([H]9)([H]10)([H]11)){=}[O+.]12"
    ">>"
    "[_A]1[C]2[C]3{=}[C]5[C]6{=}[C]7([C]8([H]9)([H]10)([H]11))[O+.]12([H]4)",
    name =
    "stabil Dienol Ion"
    " 8.9 row 1 process 1 rH CH3"
    " §R1"
)

IMS_8_9_2_CH3 = mod.Rule.fromDFS(
    s =
    "[_A]1[C]2[C]3{=}[C]4[C]5{=}[C]6([C]7([H]8)([H]9)([H]10))[O+.]11([H]12)"
    ">>"
    "[_A.]1"
    "."
    "[C]2{=}[C]3[C]4{=}[C]5[C]6([C]7([H]8)([H]9)([H]10)){=}[O+.]11([H]12)",
    name =
    "stabil Dienol Ion"
    " 8.9 row 1 process 2 alpha CH3"
    " §R1"
)

IMS_8_9_1_OCH3 = mod.Rule.fromDFS(
    s =
    "[_A]1[C]2[C]3([H]4)[C]5{=}[C]6[C]7([O]8[C]9([H10])([H]11)([H]12)){=}[O+.]13"
    ">>"
    "[_A]1[C]2[C]3{=}[C]5[C]6{=}[C]7([O]8[C]9([H]10)([H]11)([H]12))[O+.]13([H]4)",
    name =
    "stabil Dienol Ion"
    " 8.9 row 1 process 1 rH OCH3"
    " §R1"
)

IMS_8_9_2_OCH3 = mod.Rule.fromDFS(
    s =
    "[_A]1[C]2[C]3{=}[C]4[C]5{=}[C]6([O]7[C]8([H]9)([H]10)([H]11))[O+.]12([H]13)"
    ">>"
    "[_A.]1"
    "."
    "[C]2{=}[C]3[C]4{=}[C]5[C]6([O]7[C]8([H]9)([H]10)([H]11)){=}[O+.]12([H]13)",
    name =
    "stabil Dienol Ion"
    " 8.9 row 1 process 2 alpha OCH3"
    " §R1"
)

# Interpreation von Massenspektren Springer, Seite 153, Gl. 8.10
IMS_8_10 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[O+]8{=}[C]9([H]10)([H]11)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C+]5([H]6)([H]7)"
    "."
    "[O]8{=}[C]9([H]10)([H]11)",
    name =
    "Field Rule"
    " 8.10 inductive"
    ""
)

# Interpreation von Massenspektren Springer, Seite 153, Gl. 8.11
IMS_8_11 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[O+]8{=}[C]9([H]10)([H]11)"
    ">>"
    "[C]1([H]2)([H]3)[C]5([H]6)([H]7)"
    "."
    "[H]4[O+]8{=}[C]9([H]10)([H]11)",
    name =
    "Field Rule"
    " 8.11 rH"
    ""
)

# Interpreation von Massenspektren Springer, Seite 153, Gl. 8.12
IMS_8_12 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[O+]8{=}[C]9([H]10)[C]11([H]12)([H]13)([H]14)"
    ">>"
    "[C]1([H]2)([H]3)([H]4)[C+]5([H]6)([H]7)"
    "."
    "[O]8{=}[C]9([H]10)[C]11([H]12)([H]13)([H]14)",
    name =
    "Field Rule"
    " 8.12 ind"
    ""
)

# Interpreation von Massenspektren Springer, Seite 153, Gl. 8.13
IMS_8_13 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[O+]8{=}[C]9([H]10)[C]11([H]12)([H]13)([H]14)"
    ">>"
    "[C]1([H]2)([H]3)[C]5([H]6)([H]7)"
    "."
    "[H]4[O+]8{=}[C]9([H]10)[C]11([H]12)([H]13)([H]14)",
    name =
    "Field Rule"
    " 8.13 rH"
    ""
)

# Interpreation von Massenspektren Springer, Seite 154, Gl. 8.14
IMS_8_14_1 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[O+]8{=}[C]9([H]10)([H]11)"
    ">>"
    "[C]1([H]2)([H]3)[C]5([H]6)([H]7)"
    "[H+]4[O]8{=}[C]9([H]10)[C]11([H]12)([H]13)([H]14)",
    name =
    "Field Rule"
    " 8.14 r1p1 rH"
    ""
)

IMS_8_14_1b = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)[C]4([H]5)([H]6)"
    "[H+]7[O]8{=}[C]9([H]10)[C]11([H]12)([H]13)([H]14)"
    ">>"
    "[C]1([H]2)([H]3)[C]4([H]5)([H]6)"
    "[H]7[O+]8{=}[C]9([H]10)([H]11)",
    name =
    "Field Rule"
    " 8.14 r1p1 back rH"
    ""
)

IMS_8_14_2 = mod.Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)"
    "[O+]8{=}[C]9([H]10)([H]11)"
    ">>"
    "[C]1([H]2)([H]3)[C]5([H]6)([H]7)"
    "."
    "[H]4[O+]8{=}[C]9([H]10)([H]11)",
    name =
    "Field Rule"
    " 8.14 r1p2 rH"
    ""
)

# Interpreation von Massenspektren Springer, Seite 154, Gl. 8.15




IMS_chap8_examples = [
    IMS_8_1_var1_step1,
    IMS_8_1_var1_step2,
    IMS_8_1_var1_step3,
    IMS_8_1_var2_step1,
    IMS_8_1_var2_step2,
    IMS_8_1_var3_step1,
    IMS_8_1_var3_step2,
    IMS_8_2_bidirectional_down,
    IMS_8_2_bidirectional_up,
    IMS_8_2_alpha_1_1,
    IMS_8_2_ind_4_5,
    IMS_8_2_ind_2_1,
    IMS_8_2_ind_3_1,
    IMS_8_2_alpha_0_7,
    IMS_8_2_ind_2_7,
    IMS_8_2_alpha_0_6,
    IMS_8_2_rH_2_0,
    IMS_8_2_ind_1_6,
    IMS_8_2_alpha_3_8,
    IMS_8_3_ind,
    IMS_8_3_alpha,
    IMS_8_4,
    IMS_8_5_1,
    IMS_8_5_2,
    IMS_8_6_1,
    IMS_8_6_2,
    IMS_8_6_3,
    IMS_8_6_4,
    IMS_8_7_1,
    IMS_8_7_2,
    IMS_8_7_3,
    IMS_8_7_4,
    IMS_8_7_5,
    IMS_8_8_1,
    IMS_8_8_2,
    IMS_8_8_2b,
    IMS_8_8_3,
    IMS_8_9_1_CH3,
    IMS_8_9_2_CH3,
    IMS_8_9_1_OCH3,
    IMS_8_9_2_OCH3,
    IMS_8_10,
    IMS_8_11,
    IMS_8_12,
    IMS_8_13,
    IMS_8_14_1,
    IMS_8_14_1b,
    IMS_8_14_2,
]
