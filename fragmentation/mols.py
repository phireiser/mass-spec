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

butanal = smiles("CCCC=O", name = "butanal")
oleic_acid = smiles("CCCCCCCC/C=C\CCCCCCCC(=O)O", name = "(Z)-octadec-9-enoic acid")
toluene = smiles("CC1=CC=CC=C1", name= "toluene")
butylbenzene = smiles("CCCCC1=CC=CC=C1", name = "butylbenzene")
alanine = smiles("C[C@@H](C(=O)O)N", name= "(2S)-2-aminopropanoic acid")
phenylalanine = smiles("O=C(O)C(N)CC=1C=CC=CC1", name="(2S)-2-amino-3-phenylpropanoic acid")
tyrosine = smiles("C([C@@H](C(O)=O)N)C1=CC=C(O)C=C1", name="(2S)-2-amino-3-(4-hydroxyphenyl)propanoic acid")

hexane = smiles("CCCCCC", name ="hexane")
octane = smiles("CCCCCCCC", name = "octane")
butene1 = smiles("CCC=C", name = "but-1-ene")
cyclohexene = smiles("C1CCC=CC1", name = "cyclohexene")
benzene = smiles("C1=CC=CC=C1", name = "benzene") 
xylene = smiles("CC1=CC=CC=C1C", name = "1,2-xylene") 
methanol = smiles("CO", name = "methanol")
ethanol = smiles("CCO", name = "ethanol")
propanol = smiles("CCCO", name = "propan-1-ol")
tetrahydrofuran = smiles("C1CCOC1", name = "oxolane") 
acetone = smiles("CC(=O)C", name = "propan-2-one")
benzaldehyde = smiles("C1=CC=C(C=C1)C=O", name = "benzaldehyde")
butanone = smiles("CCC(=O)C", name = "butan-2-one") 
ethylAcetate = smiles("CCOC(=O)C", name = "ethyl acetate")
methylButanoate = smiles("CCCC(=O)OC", name = "methyl butanoate")
benzoicAcid = smiles("C1=CC=C(C=C1)C(=O)O", name = "benzoic acid")
chlorobenzene = smiles("C1=CC=C(C=C1)Cl", name = "chlorobenzene")
chloroform = smiles("C(Cl)(Cl)Cl", name = "chloroform")
carbonTetrachloride = smiles("C(Cl)(Cl)(Cl)Cl", name = "tetrachloromethane")
dichloromethane = smiles("C(Cl)Cl", name = "dichloromethane")
aniline = smiles("C1=CC=C(C=C1)N", name = "aniline")
methylamine = smiles("CN", name = "methanamine")
pyridine = smiles("C1=CC=NC=C1", name = "pyridine")
hexamethyldisilazane = smiles("C[Si](C)(C)N[Si](C)(C)C", name = "[dimethyl-(trimethylsilylamino)silyl]methane")
naphthalene = smiles("C1=CC=C2C=CC=CC2=C1", name = "naphthalene")
anthracene = smiles("C1=CC=C2C=C3C=CC=CC3=CC2=C1", name = "anthracene")
phenanthrene = smiles("C1=CC=C2C(=C1)C=CC3=CC=CC=C32", name = "phenanthrene")
ddt = smiles("C1=CC(=CC=C1C(C2=CC=C(C=C2)Cl)C(Cl)(Cl)Cl)Cl", name = "1-chloro-4-[2,2,2-trichloro-1-(4-chlorophenyl)ethyl]benzene") 
lindane = smiles("C1(C(C(C(C(C1Cl)Cl)Cl)Cl)Cl)Cl", name = "1,2,3,4,5,6-hexachlorocyclohexane")
polychlorinatedBiphenyls = smiles("C1=C(C(=CC(=C1Cl)Cl)Cl)C2=CC(=C(C=C2Cl)Cl)Cl", name = "1,2,4-trichloro-5-(2,4,5-trichlorophenyl)benzene") 
testosterone = smiles("C[C@]12CC[C@H]3[C@H]([C@@H]1CC[C@@H]2O)CCC4=CC(=O)CC[C@]34C", name = "(8R,9S,10R,13S,14S,17S)-17-hydroxy-10,13-dimethyl-1,2,6,7,8,9,11,12,14,15,16,17-dodecahydrocyclopenta[a]phenanthren-3-one")
cholesterol = smiles("C[C@H](CCCC(C)C)[C@H]1CC[C@@H]2[C@@]1(CC[C@H]3[C@H]2CC=C4[C@@]3(CC[C@@H](C4)O)C)C", name = "(3S,8S,9S,10R,13R,14S,17R)-10,13-dimethyl-17-[(2R)-6-methylheptan-2-yl]-2,3,4,7,8,9,11,12,14,15,16,17-dodecahydro-1H-cyclopenta[a]phenanthren-3-ol") 

common_ei_molecules = [
	butanal,
	oleic_acid,
	toluene,
	butylbenzene,
	alanine,
	phenylalanine,
	tyrosine,

	hexane,
	octane,
	butene1,
	cyclohexene,
	benzene, 
	xylene, 
	methanol,
	ethanol,
	propanol,
	tetrahydrofuran, 
	acetone,
	benzaldehyde,
	butanone, 
	ethylAcetate,
	methylButanoate,
	benzoicAcid,
	chlorobenzene,
	chloroform,
	carbonTetrachloride,
	dichloromethane,
	aniline,
	methylamine,
	pyridine,
	hexamethyldisilazane,
	naphthalene,
	anthracene,
	phenanthrene,
	ddt, 
	lindane,
	polychlorinatedBiphenyls, 
	testosterone,
	cholesterol,
]