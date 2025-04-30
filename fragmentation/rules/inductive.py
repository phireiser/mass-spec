include("../commons.py")

# https://en.wikipedia.org/wiki/Fragmentation_(mass_spectrometry)#Charge_site-initiated_cleavage
inductive_wiki = Rule.fromDFS(
	s = 
	"[C]1[C]2[O+.]3[C]4[C]5" +
	">>" +
	"[C]1[C]2[O.]3.[C]4[C+]5", 
	name = 
	"inductive cleavage f. wiki" +
	""
)

# Interpreation von Massenspektren Springer, Seite Einband, Seite 66, Gl. 4.18, 
inductive_IMS_4_18 = Rule.fromDFS(
	s =
	"[C]1[O+.]2[C]3" +
	">>" +
	"[C+]1.[C.]2[C]3",
	name = 
	"inductive cleavage odd electron 1" +
	" ^ R1Y2R3"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 with Information of 4.25 of R'
inductive_IMS_4_19_1 = Rule.fromDFS(
	s = 
	"[C]1([C]3)[C]4{=}[O+.]2" +
	">>" +
	"[C+]1.[C]3[C.]4{=}[O]2", 
	name = 
	"inductive cleavage odd electron 2" +
	" ^R1R3Y2"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 2te Variante
inductive_IMS_4_19_2 = Rule.fromDFS(# Y on left side has unpaired electron
	s = 
	"[C]1([C]3)[C+]4{=}[O.]2" +
	">>" +
	"[C+]1.[C]3[C.]4{=}[O]2", 
	name = 
	"inductive cleavage odd electron 3" +
	" ^R1R3Y2"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.20
inductive_IMS_4_20 = Rule.fromDFS(
	s = 
	"[C]1[O+]2[H]3([H]4)" +
	">>" +
	"[C+]1.[O]2[H]3([H]4)",
	name = 
	"inductive cleavage even electron 1" +
	" R1Y2"
)

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.21
inductive_IMS_4_21 = Rule.fromDFS(
	s = 
	"[C]1[O+]2{=}[C]3[H]4([H]5)" +
	">>" +
	"[C+]1.[O]2{=}[C]3[H]4([H]5)",
	name = 
	"inductive cleavage even electron 2" +
	" ^R1Y2"
)

inductive_IMS_4_22 = Rule.fromDFS(
	s = 
	"[C]1[C]2" +
	"[O+.]3" +
	"[C]4[C]5" +
	">>" +
	"[C+]1[C]2" +
	"[O.]3" +
	"[C]4[C]5",
	name = 
	"inductive cleavage odd electron 4.22" +
	""
)

inductive_IMS_4_23_1 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1[C]2[C]3[C]4.[H]5[Cl+.]6",
	name = 
	"inductive cleavage odd electron 4.23 prod 1" +
	""
)

inductive_IMS_4_23_2 = Rule.fromDFS(
	s = 
	"[C]1[C]2[C]3[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1[C]2[C]3.[C]4[H]5[Cl+.]6",
	name = 
	"inductive cleavage odd electron 4.23 prod 1" +
	""
)

inductive_IMS_4_24_1 = Rule.fromDFS(
	s = 
	"[C]1([C]2)([C]3)[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1[C]2[C]3[C]4.[H]5[Cl+.]6",
	name = 
	"inductive cleavage odd electron 4.23 prod 1" +
	""
)

inductive_IMS_4_24_2 = Rule.fromDFS(
	s = 
	"[C]1([C]2)([C]3)[C]4([H]5)[Cl+.]6" +
	">>" +
	"[C+]1([C]2)([C]3).[C]4[H]5[Cl+.]6",
	name =
	"inductive cleavage odd electron 4.23 prod 1" +
	""
)

inductive_fragmentation = [
	inductive_wiki,
	inductive_IMS_4_18,
	inductive_IMS_4_19_1,
	inductive_IMS_4_19_2,
	inductive_IMS_4_20,
	inductive_IMS_4_21,
]
inductive_fragmentation = flatten_list(inductive_fragmentation)