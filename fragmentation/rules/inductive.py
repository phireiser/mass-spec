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

inductive_fragmentation = [
	inductive_wiki,
]
inductive_fragmentation = flatten_list(inductive_fragmentation)