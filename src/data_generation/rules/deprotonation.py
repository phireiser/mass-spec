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

# Heteroatom molecular-ion formation (M -> M+.), the n-electron counterpart of
# ei_molecular_ion. In real EI the most weakly held electron is a heteroatom
# lone-pair (n) electron, so O/N/S/... ionization is the NORM, not the exception,
# and McLafferty's whole Chapter 4 ("reaction initiation at radical or charge
# sites") is built on it. ei_molecular_ion only ionizes carbon, which starved every
# rule whose left side needs an ionized heteroatom (hTransition_saturated_1/3/4,
# hTransition_unsaturated, the ester McLafferty pair): they had no substrate.
#
# One explicit rule per heteroatom rather than a single "[_A]1 >> [_A+.]1 §Y1"
# because the "_A" placeholder is expanded by apply_constraints to EVERY occurring
# atom, carbon and hydrogen included, and the "§Y" subgroup check inspects a matched
# atom's NEIGHBOURS, not the atom itself, so it does not exclude them. That form was
# measured to also ionize hydrogens ([H+.]) -- chemically meaningless species that
# just inflate the DG. Carbon is already covered by ei_molecular_ion (and a
# carbon-ionized M+. from either rule is the same graph, so it de-duplicates), so
# only the heteroatoms are listed here.
#
# Measured impact (explicit form): recovers real ions that were previously
# unreachable -- ethyl acetate m/z 43 (the experimental BASE peak) and 29; glucose's
# whole dehydration series (m/z 60, 18, ...). DG blow-up is bounded and heteroatom-
# proportional: toluene (no heteroatom) 1.0x, ethyl acetate 1.4x, glucose 2.7x.
# Molecules with no heteroatom are untouched. The largest multi-heteroatom molecules
# (steroids, disaccharides) are slow to build at baseline already, so the definitive
# no-timeout check is the corpus rebuild via regen (3-day limit), not data_gen.
_HETEROATOMS_EI = ["O", "N", "S", "P", "F", "Cl", "Br", "I"]
heteroatom_ionization = [
    mod.Rule.fromDFS(s=f"[{x}]1" ">>" f"[{x}+.]1", name=f"EI molecular ion {x}")
    for x in _HETEROATOMS_EI
]


deProtonation_all = [
    deProtonation_radical,
    deProtonation_proton,
]
