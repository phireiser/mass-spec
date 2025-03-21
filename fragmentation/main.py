include("tests/benzylAllyl_unified.py")
include("mols.py")

#universe = [butanl]
#universe = [toluene]
#universe = [butylbenzene]
#universe = [phenylalanine]

universe = tyrosine
include("derivationGraph.py")

moel_spectrum = getSpectraFRomMoelDerivationGraph(dg)
print("mol spectrum")
print(moel_spectrum)

pubchem_spectra = getSpectraFromPubChem(universe.smiles)
#print("pubmed spectra")
#print(pubchem_spectra)


from sklearn.metrics import jaccard_score

for dict_element in pubchem_spectra:
    print("\n")
    print(list(dict_element.keys())[0])
    pubchem_masses = set([int(x[0]) for x in list(dict_element.values())[0]])
    moel_masses = set([int(x[0]) for x in moel_spectrum])
    intersection = pubchem_masses & moel_masses
    print(pubchem_masses, moel_masses)
    print("intersection", intersection)
    dice = dice_coefficient(pubchem_masses, moel_masses)
    overlap = overlap_coefficient(pubchem_masses, moel_masses)
    print('dice', dice)
    print('overlap', overlap)




printGrammar()
dg.print()