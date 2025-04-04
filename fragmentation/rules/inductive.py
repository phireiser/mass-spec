include("../commons.py")
# TODO replace _Y_1, _R_1, _R_2
# R Y are subgraphs

# https://en.wikipedia.org/wiki/Fragmentation_(mass_spectrometry)#Charge_site-initiated_cleavage
inductive_wiki = Rule.fromDFS(
	"[C]1[C]2[O+.]3[C]4[C]5" +
	">>" +
	"[C]1[C]2[O.]3.[C]4[C+]5", 
	name = "inductive cleavage f. wiki")

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.18
inductive_IMS_4_18 = Rule.fromDFS(
	"[_R_1]1[_Y_1+.]2[_R_2]3" +
	">>" +
	"[_R_1+]1.[_Y_1.]2[_R_2]3", 
	name = "inductive cleavage odd electron 1")

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 with Information of 4.25 of R'
inductive_IMS_4_19_1 = Rule.fromDFS(
	"[_R_1]1([_R_2]3)[C]4{=}[_Y_1+.]2" +
	">>" +
	"[_R_1+]1.[_R_2]3[C.]4{=}[_Y_1]2", 
	name = "inductive cleavage odd electron 2")

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 2te Variante
inductive_IMS_4_19_2 = Rule.fromDFS(# Y on left side has unpaired electron
	"[_R_1]1([_R_2]3)[C+]4{=}[_Y_1.]2" +
	">>" +
	"[_R_1+]1.[_R_2]3[C.]4{=}[_Y_1]2", 
	name = "inductive cleavage odd electron 3")

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.20
inductive_IMS_4_20 = Rule.fromDFS(
	"[_R_1]1[_Y_1+]2[H]3([H]4)" +
	">>" +
	"[_R_1+]1.[_Y_1]2[H]3([H]4)",
	name = "inductive cleavage even electron 1")

# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.21
inductive_IMS_4_21 = Rule.fromDFS(
	"[_R_1]1[_Y_1+]2{=}[C]3[H]4([H]5)" +
	">>" +
	"[_R_1+]1.[_Y_1]2{=}[C]3[H]4([H]5)",
	name = "inductive cleavage even electron 2")
