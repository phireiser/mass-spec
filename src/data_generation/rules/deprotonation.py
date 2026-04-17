"""
deProtonation (H. or H+) in homolytic cleavage
source Manuel Uhlir
"""

import mod


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
	"[H+]1" "." "[_A.]2",
	name =
	"deprotonation proton"
	" §Y2"
)


# all atoms that have free electron-pairs
broad_ionization = mod.Rule.fromDFS(
	s =
	"[_A]1"
	">>"
	"[_A+.]1",
	name =
	"ionization of hetroatoms"
	" §Y1"
)

deProtonation_all = [
    deProtonation_radical,
    deProtonation_proton,
]
