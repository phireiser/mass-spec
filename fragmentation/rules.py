include("rules/benzylAllyl_ringGeneral.py")
include("rules/deprotonation.py")
include("rules/IMS_bookCover.py")
include("rules/IMS_chap4_examples.py")
include("rules/IMS_chap8_examples.py")
include("rules/wikipedia.py")


# TODO heterocyclic ring fission (HRF)
# TODO benzofuran forming fission (BFF)
# TODO quinone methide (QM) fission


ionization = [
    benzylAllyl_ionizaton, 
    wiki_ionization,
]
ionization = flatten_list(ionization)

fragmentation = [
    benzylAllyl_fragmentation,
    deProtonation_all,
    IMS_cover_fragmentation,
    IMS_chap4_examples,
    #IMS_chap8_examples,
    wiki_fragmentation,
]
fragmentation = flatten_list(fragmentation)


# contraints Label Any
constraint_string = getConstraint(occuring_commonMol_allAtoms, "A")

ionization_constrained = list()
for rule in ionization:
    ionization_constrained.append(
        addConstraints(rule, constraint_string)
    )

fragmentation_constrained = list()
for rule in fragmentation:
    fragmentation_constrained.append(
        addConstraints(rule, constraint_string)
    )


ionization_term = []
for rule in ionization_constrained:
    ionization_term.append(termFromRule(rule))

fragmentation_term = []
for rule in fragmentation_constrained:
    fragmentation_term.append(termFromRule(rule))


