include("../commons.py")
# alpha cleavage


# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Alpha-Spaltung
alpha = Rule.fromDFS(
	"[C]1[C]2({=}[O+.])[C]3[C]4" +
	">>" +
	"[C]1[C]2{#}[O+].[C.]3[C]4", 
	name = "alpha"
)


# Interpreation von Massenspektren Springer, Seite Einband, gesaettigete stelle
alpha_saturated_site_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3([C]4)[O+.]5[C]6" +
	">>" +
	"[C.]1.[C]2[C]3([C]4){=}[O+.]5[C]6",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" ^R1R3R4Y5R6"
)

# Interpreation von Massenspektren Springer, Seite Einband, gesaettigete stelle
alpha_saturated_site_2 = Rule.fromDFS(
	s =
	"[O+]1[C]2[C]3[C.]4" +
	">>" +
	"[O+.]1[C]2.[C]3[C.]4",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" ^Y1R2"
)

# Interpreation von Massenspektren Springer, Seite 60, 4.13
alpha_saturated_site_4_13_1 = Rule.fromDFS(
	s =
	"[C]1([H]2)([H]3)([H]4)" +
	"[C]5([H]6)([H]7)" +
	"[O+.]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)" +
	">>" +
	"[C.]1([H]2)([H]3)([H]4)" + 
	".[C]5([H]6)([H]7){=}" +
	"[O+]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)",
	name =
	"radical induced (alpha-)clevage for a saturated site 4.13_1" +
	""
)

alpha_saturated_site_4_13_2 = Rule.fromDFS(
	s = 
	"[C]1([H]2)([H]3)([H]4)" +
	"[C]5([H]6)([H]7)" +
	"[O+.]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)" +
	">>" +
	"[C.]1([H]2)([H]3)([H]4)" + 
	".[C+]5([H]6)([H]7){-}" +
	"[O]8[C]9([H]10)([H]11)[C]12([H]13)([H]14)([H]15)",
	name =
	"radical induced (alpha-)clevage for a saturated site 4.13_2" +
	""
)

# Interpreation von Massenspektren Springer, Seite 63, 4.17
alpha_saturated_site_4_17_1 = Rule.fromDFS(
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
	"radical induced (alpha-)clevage for a saturated site 4.17_1" +
	""
)

alpha_saturated_site_4_17_1 = Rule.fromDFS(
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
	"radical induced (alpha-)clevage for a saturated site 4.17_1" +
	""
)

alpha_saturated_site_4_17_2 = Rule.fromDFS(
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
	"radical induced (alpha-)clevage for a saturated site 4.17_2" +
	""
)

alpha_saturated_site_4_17_3 = Rule.fromDFS(
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
	"radical induced (alpha-)clevage for a saturated site 4.17_3" +
	""
)

# Interpreation von Massenspektren Springer, Seite Einband, ungesattigtes heteroatom
alpha_unsaturated_hetroatom = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3{=}[O+.]4" +
	">>" +
	"[C.]1.[C]2[C]3{#}[O+]4",
	name =
	"radical induced (alpha-)clevage for a unsaturated heteroatom" +
	" ^R1R3Y4"
)

# Interpreation von Massenspektren Springer, Seite 60, 4.14
alpha_unsaturated_hetroatom_4_14 = Rule.fromDFS(
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
	"radical induced (alpha-)clevage for a unsaturated heteroatom 4_14" +
	""
)

# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name = 
	"radical induced (alpha-)clevage for a alkene charge left" +
	" ^R1"
)

# Interpreation von Massenspektren Springer, Seite Einband, Alkene
alpha_alkene_2 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name =
	"radical induced (alpha-)clevage for a alkene charge right" +
	" ^R1"
)

# Interpreation von Massenspektren Springer, Seite 62, 4.15
alpha_alkene_4_15_1_1 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name = 
	"radical induced (alpha-)clevage for a alkene 4.15 prod 1 left charge" +
	""
)

alpha_alkene_4_15_1_2 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name =
	"radical induced (alpha-)clevage for a alkene 4.15 prod 1 right charge" +
	""
)

alpha_alkene_4_15_2_1 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C]1.[C+]2[C]3{=}[C]4",
	name = 
	"radical induced (alpha-)clevage for a alkene 4.15 prod 2 left charge" +
	""
)

alpha_alkene_4_15_2_2 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C+]2[C]3{=}[C]4",
	name = 
	"radical induced (alpha-)clevage for a alkene 4.15 prod 2 right charge"+
	""
)

alpha_alkene_4_15_3_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C+.]3[C]4[C]5[C]6[C]7[C]8" +
	">>" +
	"[C]1.[C]2{=}[C+]3[C]4[C]5[C]6[C]7[C]8",
	name = 
	"radical induced (alpha-)clevage for a alkene 4.15 2nd prod 1" +
	""
)

alpha_alkene_4_15_3_2 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3[C+.]4[C]5[C]6[C]7[C]8" +
	">>" +
	"[C.]1.[C+]2[C]3[C]4[C]5[C]6[C]7[C]8",
	name = 
	"radical induced (alpha-)clevage for a alkene 4.15 2nd prod 2" +
	""
)

alpha_fragmentation = [
	alpha,
	alpha_saturated_site_1,
	alpha_saturated_site_2,
	alpha_unsaturated_hetroatom,
	alpha_alkene_1,
	alpha_alkene_2,

	# examples:
	alpha_saturated_site_4_13_1,
	alpha_saturated_site_4_13_2,

	alpha_unsaturated_hetroatom_4_14,

	alpha_alkene_4_15_1_1,
	alpha_alkene_4_15_1_2,
	alpha_alkene_4_15_2_1,
	alpha_alkene_4_15_2_2,
	alpha_alkene_4_15_3_1,
	alpha_alkene_4_15_3_2,

	alpha_saturated_site_4_17_1,
	alpha_saturated_site_4_17_2,
	alpha_saturated_site_4_17_3,
]

alpha_fragmentation = flatten_list(alpha_fragmentation)