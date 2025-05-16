include("../commons.py")
# alpha cleavage


# https://de.wikipedia.org/wiki/Fragmentierung_(Massenspektrometrie)#Alpha-Spaltung
alpha = Rule.fromDFS(
	"[C]1[C]2({=}[O+.])[C]3[C]4" +
	">>" +
	"[C]1[C]2{#}[O+].[C.]3[C]4", 
	name = "alpha"
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.09; oder Seite Einband, Alkene
alpha_saturated_site_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3([C]4)[O+.]5[C]6" +
	">>" +
	"[C.]1.[C]2[C]3([C]4){=}[O+.]5[C]6",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" ^R1R3R4Y5R6"
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.10; oder Seite Einband, Alkene
alpha_saturated_site_2 = Rule.fromDFS(
	s =
	"[O+]1[C]2[C]3[C.]4" +
	">>" +
	"[O+.]1[C]2.[C]3[C.]4",
	name =
	"radical induced (alpha-)clevage for a saturated site" +
	" ^Y1R2"
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.11; oder Seite Einband, Alkene
alpha_unsaturated_hetroatom = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3{=}[O+.]4" +
	">>" +
	"[C.]1.[C]2[C]3{#}[O+]4",
	name =
	"radical induced (alpha-)clevage for a unsaturated heteroatom" +
	" ^R1R3Y4"
)

# Interpreation von Massenspektren Springer, Seite 59 Gl. 4.12; oder Seite Einband, Alkene
alpha_alkene_1 = Rule.fromDFS(
	s =
	"[C]1[C]2[C]3[C+.]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name = 
	"radical induced (alpha-)clevage for a alkene charge left" +
	" ^R1"
)

alpha_alkene_2 = Rule.fromDFS( 
	s = 
	"[C]1[C]2[C+.]3[C]4" +
	">>" +
	"[C.]1.[C]2{=}[C]3[C+]4",
	name =
	"radical induced (alpha-)clevage for a alkene charge right" +
	" ^R1"
)

alpha_fragmentation = [
	alpha,
	alpha_saturated_site_1,
	alpha_saturated_site_2,
	alpha_unsaturated_hetroatom,
	alpha_alkene_1,
	alpha_alkene_2,
]

alpha_fragmentation = flatten_list(alpha_fragmentation)