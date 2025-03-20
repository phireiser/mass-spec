include("tests/benzylAllyl_unified.py")
include("mols.py")

#universe = [butanl]
#universe = [toluene]
#universe = [butylbenzene]
#universe = [phenylalanine]

universe = tyrosine
include("derivationGraph.py")

spectra = getSpectraFromPubChem(universe.smiles)
print("pubmed spectra")
print(spectra)

spectra = getSpectraFRomMoelDerivationGraph(dg)
print("mol spectra")
print(spectra)


#TODO compare spectra

#printGrammar()
#dg.print()