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

butanl = smiles("CCCC=O")

oleic_acid = smiles("CCCCCCCC/C=C\CCCCCCCC(=O)O")