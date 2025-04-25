include("../commons.py")

# https://en.wikipedia.org/wiki/Fragmentation_(mass_spectrometry)#Charge_site-initiated_cleavage
inductive_wiki = Rule.fromDFS(
	"[C]1[C]2[O+.]3[C]4[C]5" +
	">>" +
	"[C]1[C]2[O.]3.[C]4[C+]5", 
	name = "inductive cleavage f. wiki")


# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.18
inductive_IMS_4_18 = (
	"[_R_1]1[_Y_1+.]2[_R_2]3" +
	">>" +
	"[_R_1+]1.[_Y_1.]2[_R_2]3", 
	"inductive cleavage odd electron 1")

inductive_IMS_4_18 = labelConstraints_dfs(
	input_rules = inductive_IMS_4_18, 
	to_replace = ["_R_1", "_R_2"],
	replacements = alkyl_stump_dfs
)

inductive_IMS_4_18 = convert2MoelRule(inductive_IMS_4_18)

inductive_IMS_4_18 = labelConstraints_gml(
	input_rules = inductive_IMS_4_18,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 with Information of 4.25 of R'
inductive_IMS_4_19_1 = (
	"[_R_1]1([_R_2]3)[C]4{=}[_Y_1+.]2" +
	">>" +
	"[_R_1+]1.[_R_2]3[C.]4{=}[_Y_1]2", 
	"inductive cleavage odd electron 2")

inductive_IMS_4_19_1 = labelConstraints_dfs(
	input_rules = inductive_IMS_4_19_1,
	to_replace = ["_R_1", "_R_2"],
	replacements = alkyl_stump_dfs
)

inductive_IMS_4_19_1 = convert2MoelRule(inductive_IMS_4_19_1)

inductive_IMS_4_19_1 = labelConstraints_gml(
	input_rules = inductive_IMS_4_19_1,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.19 2te Variante
inductive_IMS_4_19_2 = (# Y on left side has unpaired electron
	"[_R_1]1([_R_2]3)[C+]4{=}[_Y_1.]2" +
	">>" +
	"[_R_1+]1.[_R_2]3[C.]4{=}[_Y_1]2", 
	"inductive cleavage odd electron 3")

inductive_IMS_4_19_2 = labelConstraints_dfs(
	input_rules = inductive_IMS_4_19_2,
	to_replace = ["_R_1", "_R_2"],
	replacements = alkyl_stump_dfs
)

inductive_IMS_4_19_2 = convert2MoelRule(inductive_IMS_4_19_2)

inductive_IMS_4_19_2 = labelConstraints_gml(
	input_rules = inductive_IMS_4_19_2,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.20
inductive_IMS_4_20 = (
	"[_R_1]1[_Y_1+]2[H]3([H]4)" +
	">>" +
	"[_R_1+]1.[_Y_1]2[H]3([H]4)",
	"inductive cleavage even electron 1")

inductive_IMS_4_20 = labelConstraints_dfs(
	input_rules = inductive_IMS_4_20,
	to_replace = ["_R_1"],
	replacements = alkyl_stump_dfs
)

inductive_IMS_4_20 = convert2MoelRule(inductive_IMS_4_20)

inductive_IMS_4_20 = labelConstraints_gml(
	input_rules = inductive_IMS_4_20,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
)


# Interpreation von Massenspektren Springer, Seite 66, Gl. 4.21
inductive_IMS_4_21 = (
	"[_R_1]1[_Y_1+]2{=}[C]3[H]4([H]5)" +
	">>" +
	"[_R_1+]1.[_Y_1]2{=}[C]3[H]4([H]5)",
	"inductive cleavage even electron 2")

inductive_IMS_4_21 = labelConstraints_dfs(
	input_rules = inductive_IMS_4_21,
	to_replace = ["_R_1"],
	replacements = alkyl_stump_dfs
)

inductive_IMS_4_21 = convert2MoelRule(inductive_IMS_4_21)

inductive_IMS_4_21 = labelConstraints_gml(
	input_rules = inductive_IMS_4_21,
	rpl_dict = {
		"_Y_1": heteroAtoms,
	}
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