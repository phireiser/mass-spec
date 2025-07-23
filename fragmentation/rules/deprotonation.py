import mod

# deProtonation (H. or H+) in homolytic cleavage
# source Manuel Uhlir

deProtonation_radical = mod.Rule.fromDFS(
	s = 
	"[H]1[_A]2"
	">>"
	"[H.]1" "." "[_A+]2", 
	name = 
	"deprotonation radical"
	" §Y2"
)


deProtonation_proton = mod.Rule.fromDFS(
	s = 
	"[H]1[_A]2"
	">>"
	"[H+]1.[_A.]2", 
	name = 
	"deprotonation proton"
	" §Y2"
)


deProtonation_all = [
    deProtonation_radical,
    deProtonation_proton,
]