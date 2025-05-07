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

# Interpreation von Massenspektren Springer, Seite 59, Gl. 4.8
sigma_alkane_4_8 = Rule.fromDFS(
	s =
	"[C+.]1" +
	"([C]2([H]3)([H]4)([H]5))" +
	"([C]6([H]7)([H]8)([H]9))" +
	"([C]10([H]11)([H]12)([H]13))" +
	"[C]14([H]15)([H]16)" +
	"[C]20([H]21)([H]22)([H]23)" +
	">>" +
	"[C+]1" +
	"([C]2([H]3)([H]4)([H]5))" +
	"([C]6([H]7)([H]8)([H]9))" +
	"([C]10([H]11)([H]12)([H]13))" +
	".[C.]14([H]15)([H]16)" + # radcial can be anywhere in 2nd fragment
	"[C]17([H]18)([H]19)([H]20)",
	name =
	"dissoziation of a sigma bond for alkans 4.8"+
	""
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
	sigma_alkane_4_8,
]

sigma_fragmentation = flatten_list(sigma_fragmentation)