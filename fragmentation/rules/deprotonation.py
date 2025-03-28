# deProtonation (H. or H+) in homolytic cleavage
# source Manuel Uhlir

deProtonation_radical =  Rule.fromDFS(
	"[H]1[_A]2" +
	">>" +
	"[H.]1.[_A+]2", 
	name = "Deprotonation radical")

deProtonation_proton =  Rule.fromDFS(
	"[H]1[_A]2" +
	">>" +
	"[H+]1.[_A.]2", 
	name = "Deprotonation proton")

deProtonation_proton = labelConstraints(deProtonation_proton, 
	rpl_dict = {
		"_A" : ['N', 'O']
	}
)

deProtonation_radical= labelConstraints(deProtonation_radical, 
rpl_dict = {
	"_A" : ['N', 'O']
})


deProtonation_all = [
    deProtonation_radical,
    deProtonation_proton,
]