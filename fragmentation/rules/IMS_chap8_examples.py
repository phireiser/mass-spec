# Interpreation von Massenspektren Springer, Seite 143, Gl. 8.1
IMS_8_1_var1_step1 = Rule.fromDFS(
    s =
    "[H]1[C]2[C]3[H]4[C]5{=}[C+.]6" +
    ">>" +
    "[H]1.[C]2[C]3[C]4{=}[C]5[C+.]6",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 var1 step 1" +
	""
)

IMS_8_1_var1_step2 = Rule.fromDFS(
    s =
    "[H]1.[C]2[C]3[C]4{=}[C]5[C+.]6" +
    ">>" +
    "[H]1[C.]2.[C]3{=}[C]4[C+]5[C]6",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 var1 step 2" +
	""
)

IMS_8_1_var1_step3 = Rule.fromDFS(
    s =
    "[C]1{=}[C]2[C+]3[C]4" +
    ">>" +
    "[C]1{=}[C]2[C+]3[C]4",
    name =
    "monomolecular ion-cleavage" +
	" 8.1 var1 step 3" +
	""
)