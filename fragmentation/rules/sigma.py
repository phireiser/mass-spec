include("../commons.py")
# sigma cleavage

# Interpreation von Massenspektren Springer, Seite 58, Gl. 4.7
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

sigma_fragmentation = [
    sigma_alkane,
    sigma_lowIE,
]

sigma_fragmentation = flatten_list(sigma_fragmentation)