include("../commons.py")
# sigma cleavage

# Interpreation von Massenspektren Springer, Seite 58, Gl. 4.7 und Seite Einband
sigma_alkane = (
	"[_R_1+.]1[C]2[_R_2]3[_R_3]4[_R_4]5" +
	">>" +
	"[_R_1.]1.[C+]2[_R_2]3[_R_3]4[_R_4]5",
	"dissoziation of a sigma bond for alkans")

sigma_alkane = labelConstraints_dfs(
	input_rules = sigma_alkane, 
	to_replace = ["_R_1", "_R_2", "_R_3", "_R_4"],
	replacements = alkyl_stump_dfs
)

sigma_alkane = convert2MoelRule(sigma_alkane)

# Interpreation von Massenspektren Springer, Seite 59, Gl. 4.8
sigma_alkane_4_8 = ( 
	"[C+.]1" +
	"([C]2([H]3)([H]4)([H]5))" +
	"([C]6([H]7)([H]8)([H]9))" +
	"([C]10([H]11)([H]12)([H]13)" +
	"[C]14([H]15)([H]16)" +
	"[C]20([H]21)([H]22)([H]23)" +
	">>" +
	"[C+]1" +
	"([C]2([H]3)([H]4)([H]5))" +
	"([C]6([H]7)([H]8)([H]9))" +
	"([C]10([H]11)([H]12)([H]13))" +
	".[C.]14([H]15)([H]16)" + # radcial can be anywhere in 2nd fragment
	"[C]17([H]18)([H]19)([H]20)",
	"dissoziation of a sigma bond for alkans 4.8")

sigma_alkane_4_8 = convert2MoelRule(sigma_alkane_4_8)


# Interpreation von Massenspektren Springer, Seite Einband, element with low IE
sigma_lowIE = (
	"[_R_1+.]1[I]2" +
	">>" +
	"[_R_1.]1.[I+]2",
	"dissoziation of a sigma bond for Elements with low IE")

sigma_lowIE = labelConstraints_dfs(
	input_rules = sigma_lowIE, 
	to_replace = ["_R_1"],
	replacements = alkyl_stump_dfs
)

sigma_lowIE = convert2MoelRule(sigma_lowIE)

sigma_fragmentation = [
    sigma_alkane,
    sigma_lowIE,
	sigma_alkane_4_8,
]

sigma_fragmentation = flatten_list(sigma_fragmentation)