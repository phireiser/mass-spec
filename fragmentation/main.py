import pandas as pd
from pprint import pprint

#include("tests/benzylAllyl_unified.py")
include("mols.py")

heteroAtoms = [
    "He","Li","Be","B","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca",
    "Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb",
    "Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe",
    "Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
    "Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra",
    "Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es"
]

occuring_hetroAtoms = set()
for m in common_ei_molecules:
    for ha in heteroAtoms:
        if m.vLabelCount(ha) > 0:
            occuring_hetroAtoms.add(ha)

heteroAtoms = occuring_hetroAtoms # only create rules for occuring hetroAtoms

include("commons.py")
include("strategy.py")
include("rules.py")


ionization = [
    benzylAllyl_ionizaton, 
    deProtonation_all,
    mcLafferty_ionization,
    retroDielsAdler_ionization, 
]

fragmentation = [
    alpha_fragmentation,
    benzylAllyl_fragmentation, 
    inductive_fragmentation,
    mcLafferty_fragmenation,
    rearrangements,
    retroDielsAdler_fragmentation, 
    sigma_fragmentation,
]

allLoadedRules_dict = dict()
for rulelist in ionization + fragmentation:
    for e in rulelist:
        print(e)
        allLoadedRules_dict[e.id] = e.name

allActiveRules = set()

for m in common_ei_molecules:
    print("\n")
    print("mol spectrum of", m.name)
    strategy = makeStrategy(universe=[m], ionization=ionization, fragmentation=fragmentation)
    dg = DG(graphDatabase=[m])
    dg.build().execute(strategy)

    pubchemSpectra = getSpectraFromPubChem(m.smiles)
    moelSpectrum_dict = getSpectraFRomMoelDerivationGraph(dg)
    moelSpectrum_df = pd.DataFrame(moelSpectrum_dict, columns=["mass", "intensity", "rules"])

    for pubchemSpectrum in pubchemSpectra:

        pubchem_masses = set([int(x[0]) for x in list(pubchemSpectrum.values())[0]])
        moel_masses = set([int(x[0]) for x in moelSpectrum_dict])

        #print("masses:\t", "pubchem", pubchem_masses, "moel", moel_masses)
        #print("intersection", pubchem_masses & moel_masses)
        #print('dice', dice_coefficient(pubchem_masses, moel_masses))
        #print('overlap', overlap_coefficient(pubchem_masses, moel_masses))

        # collect rules that created matching masses threshold +/- 1
        if len(moelSpectrum_df) > 0:
            rulesActiveHere = moelSpectrum_df[
                moelSpectrum_df["mass"].apply(
                    lambda m: any(abs(m - cm) <= 1.0 for cm in pubchem_masses)
                )
            ]["rules"]
            
            for rule_group in rulesActiveHere:
                allActiveRules.update(rule_group)

print("\n\n")
print("allUsedRules")
pprint(allLoadedRules_dict)
print("allActiveRules", allActiveRules)
print("unusedRules", set(allLoadedRules_dict.keys()) - allActiveRules)







#printGrammar(inGraphs = common_ei_molecules, inRules = ionization + fragmentation)
#dg.print()

#printRules(ionization + fragmentation)

