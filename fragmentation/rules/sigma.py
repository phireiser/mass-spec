include("../commons.py")
# TODO replace _Y_1, _R_1, _R_2
# R Y are subgraphs

# sigma cleavage

# Interpreation von Massenspektren Springer, Seite 58, Gl. 4.7
sigma_alkane = Rule.fromDFS(
	"[_R_1+.]1[C]2[_R_2]3[_R_3]4[_R_4]5" +
	">>" +
	"[_R_1.]1.[C+]2[_R_2]3[_R_3]4[_R_4]5",
	name = "dissoziation of a sigma bond for alkans")

# Interpreation von Massenspektren Springer, Seite Einband, element with low IE
sigma_lowIE = Rule.fromDFS(
	"[_R_1+.]1[I]2" +
	">>" +
	"[_R_1.]1.[I+]2",
	name = "dissoziation of a sigma bond for Elements with low IE")


