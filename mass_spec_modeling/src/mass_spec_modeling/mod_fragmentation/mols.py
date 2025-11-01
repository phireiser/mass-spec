"""
definition of molecules
"""

import mod
from .utils.term_transfers import term_from_graph
from .utils.constrain import all_occuring, allAtoms


macLafferty = mod.Graph.fromGMLString(
"""graph [
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
]""",
name = "McLafferty Dummy Structure"
)

butanal = mod.Graph.fromSMILES("CCCC=O", name = "butanal")
oleic_acid = mod.Graph.fromSMILES("CCCCCCCCC=CCCCCCCCC(=O)O", name = "(Z)-octadec-9-enoic acid")
toluene = mod.Graph.fromSMILES("CC1=CC=CC=C1", name= "toluene")
butylbenzene = mod.Graph.fromSMILES("CCCCC1=CC=CC=C1", name = "butylbenzene")
alanine = mod.Graph.fromSMILES("C[C@@H](C(=O)O)N", name= "(2S)-2-aminopropanoic acid")
phenylalanine = mod.Graph.fromSMILES("O=C(O)C(N)CC=1C=CC=CC1", name="(2S)-2-amino-3-phenylpropanoic acid")
tyrosine = mod.Graph.fromSMILES(
	"C([C@@H](C(O)=O)N)C1=CC=C(O)C=C1",
	name="(2S)-2-amino-3-(4-hydroxyphenyl)propanoic acid"
)
hexane = mod.Graph.fromSMILES("CCCCCC", name ="hexane")
octane = mod.Graph.fromSMILES("CCCCCCCC", name = "octane")
butene1 = mod.Graph.fromSMILES("CCC=C", name = "but-1-ene")
cyclohexene = mod.Graph.fromSMILES("C1CCC=CC1", name = "cyclohexene")
benzene = mod.Graph.fromSMILES("C1=CC=CC=C1", name = "benzene")
xylene = mod.Graph.fromSMILES("CC1=CC=CC=C1C", name = "1,2-xylene")
methanol = mod.Graph.fromSMILES("CO", name = "methanol")
ethanol = mod.Graph.fromSMILES("CCO", name = "ethanol")
propanol = mod.Graph.fromSMILES("CCCO", name = "propan-1-ol")
tetrahydrofuran = mod.Graph.fromSMILES("C1CCOC1", name = "oxolane")
acetone = mod.Graph.fromSMILES("CC(=O)C", name = "propan-2-one")
benzaldehyde = mod.Graph.fromSMILES("C1=CC=C(C=C1)C=O", name = "benzaldehyde")
butanone = mod.Graph.fromSMILES("CCC(=O)C", name = "butan-2-one")
ethylAcetate = mod.Graph.fromSMILES("CCOC(=O)C", name = "ethyl acetate")
methylButanoate = mod.Graph.fromSMILES("CCCC(=O)OC", name = "methyl butanoate")
benzoicAcid = mod.Graph.fromSMILES("C1=CC=C(C=C1)C(=O)O", name = "benzoic acid")
chlorobenzene = mod.Graph.fromSMILES("C1=CC=C(C=C1)Cl", name = "chlorobenzene")
chloroform = mod.Graph.fromSMILES("C(Cl)(Cl)Cl", name = "chloroform")
carbonTetrachloride = mod.Graph.fromSMILES("C(Cl)(Cl)(Cl)Cl", name = "tetrachloromethane")
dichloromethane = mod.Graph.fromSMILES("C(Cl)Cl", name = "dichloromethane")
aniline = mod.Graph.fromSMILES("C1=CC=C(C=C1)N", name = "aniline")
methylamine = mod.Graph.fromSMILES("CN", name = "methanamine")
pyridine = mod.Graph.fromSMILES("C1=CC=NC=C1", name = "pyridine")
hexamethyldisilazane = mod.Graph.fromSMILES(
	"C[Si](C)(C)N[Si](C)(C)C",
	name = "[dimethyl-(trimethylsilylamino)silyl]methane"
)
naphthalene = mod.Graph.fromSMILES("C1=CC=C2C=CC=CC2=C1", name = "naphthalene")
anthracene = mod.Graph.fromSMILES("C1=CC=C2C=C3C=CC=CC3=CC2=C1", name = "anthracene")
phenanthrene = mod.Graph.fromSMILES("C1=CC=C2C(=C1)C=CC3=CC=CC=C32", name = "phenanthrene")
ddt = mod.Graph.fromSMILES(
	"C1=CC(=CC=C1C(C2=CC=C(C=C2)Cl)C(Cl)(Cl)Cl)Cl",
	name = "1-chloro-4-[2,2,2-trichloro-1-(4-chlorophenyl)ethyl]benzene"
)
lindane = mod.Graph.fromSMILES("C1(C(C(C(C(C1Cl)Cl)Cl)Cl)Cl)Cl", name = "1,2,3,4,5,6-hexachlorocyclohexane")
polychlorinatedBiphenyls = mod.Graph.fromSMILES(
	"C1=C(C(=CC(=C1Cl)Cl)Cl)C2=CC(=C(C=C2Cl)Cl)Cl",
	name = "1,2,4-trichloro-5-(2,4,5-trichlorophenyl)benzene"
)
testosterone = mod.Graph.fromSMILES(
	"C[C@]12CC[C@H]3[C@H]([C@@H]1CC[C@@H]2O)CCC4=CC(=O)CC[C@]34C",
	name = "(8R,9S,10R,13S,14S,17S)-17-hydroxy-10,13-dimethyl-1,2,6,7,8,9,11,12,14,15,16,17-"
	"dodecahydrocyclopenta[a]phenanthren-3-one"
)
cholesterol = mod.Graph.fromSMILES(
	"C[C@H](CCCC(C)C)[C@H]1CC[C@@H]2[C@@]1(CC[C@H]3[C@H]2CC=C4[C@@]3(CC[C@@H](C4)O)C)C",
	name = "(3S,8S,9S,10R,13R,14S,17R)-10,13-dimethyl-17-[(2R)-6-methylheptan-2-yl]-"
	"2,3,4,7,8,9,11,12,14,15,16,17-dodecahydro-1H-cyclopenta[a]phenanthren-3-ol"
)
linolenicAcid = mod.Graph.fromSMILES(
	"O=C(O)CCCCCCCC=CCC=CCC=CCC",
	"9,12,15-Octadecatrienoic acid, (9Z,12Z,15Z)"
)

common_ei_molecules = [
	butanal,
#	oleic_acid,
	toluene,
	butylbenzene,
	alanine,
	phenylalanine,
	tyrosine,

#	hexane, # impractical
#	octane, # impractical
#	butene1, # impractical
	cyclohexene,
	benzene,
	xylene,
#	methanol, # impractical
#	ethanol, # impractical
#	propanol, # impractical
	tetrahydrofuran,
#	acetone, # impractical
	benzaldehyde,
	butanone,
	ethylAcetate,
	methylButanoate,
	benzoicAcid,
	chlorobenzene,
#	chloroform, # impractical
	carbonTetrachloride, # impractical
#	dichloromethane, # impractical
	aniline,
#	methylamine, # impractical
	pyridine,
#	hexamethyldisilazane, # impractical
	naphthalene,
	anthracene,
	phenanthrene,
	ddt,
	lindane,
	polychlorinatedBiphenyls,
	testosterone, # needs a lot of memory
	#cholesterol, # for the saturation rule extention it needs more memory, I assume the mol is too big, stopt at 20GB mem
	#linolenicAcid, # needs a lot of memory 30% local
]

common_ei_mol_term = []
for m in common_ei_molecules:
    common_ei_mol_term.append(term_from_graph(m))

small_ei_mol_term = [
    term_from_graph(x) for x in [
        #toluene,
        butanal,
    	#butylbenzene,
    	#phenylalanine,
    	#tyrosine,
        #benzoicAcid,
    	#chlorobenzene,
      #  polychlorinatedBiphenyls,
      #  anthracene,
    ]
]

occuring_commonMol_allAtoms = all_occuring(common_ei_molecules, allAtoms)
