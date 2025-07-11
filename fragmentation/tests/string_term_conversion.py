include('../rules.py')
include("../mols.py")

ionization = [
    benzylAllyl_ionizaton, 
    wiki_ionization,
]
ionization = flatten_list(ionization)

fragmentation = [
    #alpha_fragmentation,
    benzylAllyl_fragmentation,
    IMS_cover_fragmentation,
    deProtonation_all,
    IMS_examples,
    #inductive_fragmentation,
    #mcLafferty_fragmenation,
    rearrangements,
    #retroDielsAdler_fragmentation, 
    wiki_fragmentation,
]
fragmentation = flatten_list(fragmentation)

fragmentation_term =[]
for r in fragmentation:
    fragmentation_term.append(termFromRule(r))

ionization_term =[]
for r in ionization:
    ionization_term.append(termFromRule(r))

common_ei_mol_term = []
for m in common_ei_molecules:
    common_ei_mol_term.append(termFromGraph(m))



fragmentation_back =[]
for r in fragmentation_term:
    fragmentation_back.append(ruleFromTerm(r))

ionization_back =[]
for r in ionization_term:
    ionization_back.append(ruleFromTerm(r))

common_ei_mol_back = []
for m in common_ei_mol_term:
    common_ei_mol_back.append(graphFromTerm(m))



for original, back in zip(fragmentation, fragmentation_back):
    try:
        assert multiline_equal(original.getGMLString(), back.getGMLString())
    except AssertionError:
        if ".." in original.getGMLString(): # dirty double radical test
            print("double radical, mol can't handle this")        
        else:
            print("something else must be going on")
            raise

for original, back in zip(ionization, ionization_back):
    try:
        assert multiline_equal(original.getGMLString(), back.getGMLString())
    except AssertionError:
        if ".." in original.getGMLString(): # dirty double radical test
            print("double radical, mol can't handle this")        
        else:
            print("something else must be going on")
            raise

for original, back in zip(common_ei_molecules, common_ei_mol_back):
    try:
        assert multiline_equal(original.getGMLString(), back.getGMLString())
    except AssertionError:
        if ".." in original.getGMLString(): # dirty double-radical test
            print("double radical, mol can't handle this")        
        else:
            print("something else must be going on")
            raise