# Interpreation von Massenspektren Springer, Seite 143, Gl. 8.1
IMS_8_1_var1_step1 = Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12){=}[C+.]13([H]14)([H]15)" +
    ">>" +
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9){=}[C]11([H]12)[C+.]13([H]14)([H]15)([H]10)",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 rH -0.6" +
	""
)

IMS_8_1_var1_step2 = Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9){=}[C]10([H]11)[C+.]12([H]13)([H]14)([H]15)" +
    ">>" +
    "[H]1[C.]2([H]3)([H]4).[C]5([H]6){=}[C]8([H]9)[C+]10([H]11)([H]7)[C]12([H]13)([H]14)([H]15)",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 alpha 1.0" +
	""
)

IMS_8_1_var1_step3 = Rule.fromDFS(
    s =
    "[C]1([H]2){=}[C]3([H]4)[C+]5([H]6)([H]7)[C]8([H]9)([H]10)([H]11)" +
    ">>" +
    "[c]1([H]2)[c+]3([H]4)[c]5([H]6){-}1.[H]7[C]8([H]9)([H]10)([H]11)", # https://en.wikipedia.org/wiki/Cyclopropenium_ion
    name =
    "monomolecular ion-cleavage" +
	" 8.1 rH 2.5" +
	""
)

IMS_8_1_var2_step1 = Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12){=}[C+.]13([H]14)([H]15)" +
    ">>" +
    "[H]1[C]2([H]3)([H]4)[C.]5([H]6)([H]7).[C+]8([H]9)([H]10)[C]11([H]12){=}[C]13([H]14)([H]15)",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 alpha 1.7" +
	""
)

IMS_8_1_var2_step2 = Rule.fromDFS(
    s =
    "[C+]1([H]2)([H]3)[C]4([H]5){=}[C]6([H]7)([H]8)" +
    ">>" +
    "[c+]1([H]2)[c]4([H]5)[c]6([H]7){-}1.[H]3[H]8", # charge somewhere in ring # https://en.wikipedia.org/wiki/Cyclopropenium_ion
    name =
    "monomolecular ion-cleavage" +
	" 8.1 rH 3.0" +
	""
)

IMS_8_1_var3_step1 = Rule.fromDFS(
    s =
    "[H]1[C]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12){=}[C+.]13([H]14)([H]15)" +
    ">>" +
    "[C.]2([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+]11([H]12)[C]13([H]14)([H]15)([H]1)",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 rH 0.3" +
	""
)

IMS_8_1_var3_step2 = Rule.fromDFS(
    s =
    "[C.]1([H]2)([H]3)[C]4([H]5)([H]6)[C]7([H]8)([H]9)[C+]10([H]11)[C]12([H]13)([H]14)([H]15)" +
    ">>" +
    "[C]1([H]2)([H]3)[C]4([H]5)([H]6).[C]7([H]8)([H]9)([H]11)[C]10([H]13){=}[C+.]12([H]14)([H]15)",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 alpha 1.1" +
	""
)

# Interpreation von Massenspektren Springer, Seite 144, Gl. 8.2
IMS_8_2_bidirectional_down = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14([C]15([H]16)([H]17)([H]18)){=}[O+]19([H]7)",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 bidirectional down" +
	""
)

IMS_8_2_bidirectional_up = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]7([H]8)([H]9)[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+]18([H]19)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]19)[C]7([H]8)([H]9)[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+.]18",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 bidirectional up" +
	""
)

# 1st line
IMS_8_2_alpha_1_1 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C.]11([H]12)([H]13).[C]15([H]16)([H]17)([H]18)[C]14{#}[O+]19",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 alpha 1.1" +
	""
)

IMS_8_2_ind_4_5 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5{#}[O+]6" +
    ">>" +
    "[C+]1([H]2)([H]3)([H]4).[C]5{=}[O]6",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 inductive 4.5" +
	""
)

# 2nd line
IMS_8_2_ind_2_1 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+]11([H]12)([H]13).[C]15([H]16)([H]17)([H]18)[C.]14{=}[O]19",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 inductive 2.1" +
	""
)

IMS_8_2_ind_3_1 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+]11([H]12)([H]13)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C+]5([H]6)([H]7).[C]8([H]9)([H]10)[C]11([H]12)([H]13)",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 inductive 3.1" +
	""
)

# 3rd line
IMS_8_2_alpha_0_7 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14([C]15([H]16)([H]17)([H]18)){=}[O+.]19" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14[O+]19.[C.]15([H]16)([H]17)([H]18)",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 alpha 0.7" +
	""
)

IMS_8_2_ind_2_7 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+]11([H]12)([H]13)[C]14[O+]15" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+]11([H]12)([H]13).[C]14[O]15",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 inductive 2.7" +
	""
)

# 4th line
IMS_8_2_alpha_0_6 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]7([H]8)([H]9)[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+]18([H]19)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6){=}[C]7([H]8)([H]9).[C]10([H]11)([H]12){=}[C]13([C]14([H]15)([H]16)([H]17)){=}[O+.]18([H]19)",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 alpha 0.6" +
	""
)

IMS_8_2_rH_2_0 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3){=}[C]4([C]5([H]6)([H]7)([H]8)){=}[O+.]9([H]10)" +
    ">>" +
    "[C.]1([H]2)([H]3)([H]10).[C]4([C]5([H]6)([H]7)([H]8))[O+]9",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 rH 2.0" +
	""
)

# 5th line
IMS_8_2_ind_1_6 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C.]5([H]6)[C]7([H]8)([H]9)[C]10([H]11)([H]12)[C]13([C]14([H]15)([H]16)([H]17)){=}[O+]18([H]19)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C+.]5([H]6)[C]7([H]8)([H]9).[C]10([H]11)([H]12){=}[C]13([C]14([H]15)([H]16)([H]17))[O]18([H]19)",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 inductive 1.6" +
	""
)

IMS_8_2_alpha_3_8 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C+.]5([H]6)[C]7([H]8)([H]9)" +
    ">>" +
    "[C]1([H]2)([H]3)[C+]5([H]6)[C]7([H]8)([H]9).[H.]4",
    name =
    "monomolecular ion-cleavage" +
	" 8.2 alpha 3.8" +
	""
)

# Interpreation von Massenspektren Springer, Seite 147, Gl. 8.3
IMS_8_3_ind = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+.]11([H]12)([H]13)[O]14[C]15([H]16)([H]17)([H]18)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+]11([H]12)([H]13).[O+]14[C]15([H]16)([H]17)([H]18)",
    name =
    "monomolecular ion-cleavage" +
	" 8.3 ind" +
	""
)

IMS_8_3_alpha = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+.]8([H]9)([H]10)[C]11([H]12)([H]13)[O]14[C]15([H]16)([H]17)([H]18)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+]8([H]9)([H]10).[C]11([H]12)([H]13){=}[O+]14[C]15([H]16)([H]17)([H]18)",
    name =
    "monomolecular ion-cleavage" +
	" 8.3 alpha" +
	""
)

# Interpreation von Massenspektren Springer, Seite 147, Gl. 8.4
IMS_8_4 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+.]11([H]12)([H]13)[C]14[O]15[C]16([H]17)([H]18)([H]19)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C+.]11([H]12)([H]13).[C]16([H]17)([H]18)([H]19)[C]14[O+]15",
    name =
    "monomolecular ion-cleavage" +
	" 8.4 ind" +
	""
)

# Interpreation von Massenspektren Springer, Seite 148, Gl. 8.5
IMS_8_5_1 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[C]14([H]15)([H]16)[C]17([H]18)([H]19){=}[O+.]20" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+.]8([H]9){=}[C]11([H]12)([H]13).[C]14([H]15)([H]16){=}[C]17([H]18)([H]19)[O+.]20[H]10",
    name =
    "monomolecular ion-cleavage" +
	" 8.5 row 1" +
	""
)

IMS_8_5_2 = Rule.fromDFS(
    s =
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C]8([H]9)([H]10)[C]11([H]12)([H]13)[O]14([H]15)([H]16)[C]17([H]18)([H]19){=}[C+.]20([H]21)([H]22)" +
    ">>" +
    "[C]1([H]2)([H]3)([H]4)[C]5([H]6)([H]7)[C+.]8([H]9){=}[C]11([H]12)([H]13).[O+.]14([H]15)([H]16){=}[C]17([H]18)([H]19)[C]20([H]21)([H]22)([H]10)",
    name =
    "monomolecular ion-cleavage" +
	" 8.5 row 2" +
	""
)

# Interpreation von Massenspektren Springer, Seite 149, Gl. 8.6

