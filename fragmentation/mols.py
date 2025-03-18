macLafferty = graphGMLString("""graph [
	node [ id 1 label "C" ]
	node [ id 2 label "C" ]
	node [ id 3 label "C" ]
	node [ id 4 label "C" ]
	node [ id 5 label "H" ]
	node [ id 6 label "O" ]
	edge [ source 1 target 2 label "-" ]
	edge [ source 2 target 3 label "-" ]
	edge [ source 3 target 4 label "-" ]
	edge [ source 4 target 5 label "-" ]
	edge [ source 1 target 6 label "=" ]
]""", name="McLafferty Dummy Structure")

butanl = smiles("CCCC=O", name = "butanl")
oleic_acid = smiles("CCCCCCCC/C=C\CCCCCCCC(=O)O", name = "oleic acid")
toluene = smiles("CC1=CC=CC=C1", name= "toluene")
butylbenzene = smiles("CCCCC1=CC=CC=C1", name = "butylbenzene ")
alanine = smiles("C[C@@H](C(=O)O)N", name= "alanine")
phenylalanine = smiles("O=C(O)C(N)CC=1C=CC=CC1", name="phenylalanine")
tyrosine = smiles("C([C@@H](C(O)=O)N)C1=CC=C(O)C=C1", name="tyrosine")