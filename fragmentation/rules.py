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

ionization_term =[]
for r in ionization:
    ionization_term.append(termFromRule(r))

fragmentation = [
    benzylAllyl_fragmentation,
    deProtonation_all,
    IMS_cover_fragmentation,
    IMS_examples, 
    wiki_fragmentation,
]
fragmentation = flatten_list(fragmentation)

fragmentation_term =[]
for r in fragmentation:
    fragmentation_term.append(termFromRule(r))