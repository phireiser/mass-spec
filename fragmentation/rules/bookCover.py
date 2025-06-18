# Interpreation von Massenspektren Springer, Seite Einband, element with low IE
sigma_lowIE = Rule.fromDFS(
	s =
	"[C+.]1[I]2" +
	">>" +
	"[C.]1.[I+]2",
	name =
	"dissoziation of a sigma bond for Elements with low IE" +
	" §R1"
)


cover_fragmentation = [
    sigma_lowIE,
]