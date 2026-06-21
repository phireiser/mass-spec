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


# Electron-impact molecular-ion formation (M -> M+.): removal of a single
# electron, localized on a carbon, keeping every atom and bond intact. Unlike the
# dissociative ionization rules (which immediately lose H or CH3), this retains
# the full mass, so the intact molecular ion is generated for any organic molecule
# -- the root of the EI fragmentation tree. Heteroatom-localized ionization is
# handled separately by the mechanism-specific rules (e.g. McLafferty's
# ml_ionization). Fires once per carbon, giving a few mass-equal M+. isomers that
# the spectrum step deduplicates by mass.
ei_molecular_ion = mod.Rule.fromDFS(
	s =
	"[C]1"
	">>"
	"[C+.]1",
	name =
	"EI molecular ion"
	""
)

deProtonation_all = [
    deProtonation_radical,
    deProtonation_proton,
]
