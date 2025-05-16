include("../commons.py")
# sigma cleavage

# Interpreation von Massenspektren Springer, Seite 58, Gl. 4.7 und Seite Einband
sigma_alkane = Rule.fromDFS(
	s = 
	"[C+.]1[C]2[C]3[C]4[C]5" +
	">>" +
	"[C.]1.[C+]2[C]3[C]4[C]5",
	name = 
	"dissoziation of a sigma bond for alkans" +
	" ^R1R3R4R5"
	
)

# Interpreation von Massenspektren Springer, Seite Einband, element with low IE
sigma_lowIE = Rule.fromDFS(
	s =
	"[C+.]1[I]2" +
	">>" +
	"[C.]1.[I+]2",
	name =
	"dissoziation of a sigma bond for Elements with low IE" +
	" ^R1"
)

sigma_fragmentation = [
    sigma_alkane,
    sigma_lowIE,
]

sigma_fragmentation = flatten_list(sigma_fragmentation)