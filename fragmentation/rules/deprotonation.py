# deProtonation (H. or H+) in homolytic cleavage
# source Manuel Uhlir

include("../commons.py")

deProtonation_radical = Rule.fromDFS(
	s = 
	"[H]1[O]2" +
	">>" +
	"[H.]1.[O+]2", 
	name = 
	"Deprotonation radical" +
	" ^Y2"
)


deProtonation_proton = Rule.fromDFS(
	s = 
	"[H]1[O]2" +
	">>" +
	"[H+]1.[O.]2", 
	name = 
	"Deprotonation proton" +
	" Y2"
)


deProtonation_all = [
    deProtonation_radical,
    deProtonation_proton,
]

deProtonation_all = flatten_list(deProtonation_all)