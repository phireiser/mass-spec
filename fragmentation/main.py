#include("tests/benzylAllyl_unified.py")
include("mols.py")
include("strategy.py")
include("rules.py")

import pandas as pd

ionization = [benzylAllyl_ionizaton, dielsAdler_ionization, mcLafferty_ionization]
fragmentation = [benzylAllyl_fragmentation, dielsAdler_fragmentation, mcLafferty_fragmenation, alpha_fragmentation]

allUsedRules_dict = dict()
for i in ionization + fragmentation:
    for e in i:
        allUsedRules_dict[e.id] = e.name

allActiveRules = set()

for m in common_ei_molecules:
    print("\n")
    print("mol spectrum of", m.name)
    strategy = makeStrategy(universe=m, ionization=ionization, fragmentation=fragmentation)
    dg = DG(graphDatabase=[m])
    dg.build().execute(strategy)

    pubchemSpectra = getSpectraFromPubChem(m.smiles)
    moelSpectrum_dict = getSpectraFRomMoelDerivationGraph(dg)
    moelSpectrum_df = pd.DataFrame(moelSpectrum_dict, columns=["mass", "intensity", "rules"])


    for pubchemSpectrum in pubchemSpectra:

        pubchem_masses = set([int(x[0]) for x in list(pubchemSpectrum.values())[0]])
        moel_masses = set([int(x[0]) for x in moelSpectrum_dict])
        commonMasses = pubchem_masses & moel_masses
        #print("masses:\t", "pubchem", pubchem_masses, "moel", moel_masses)
        #print("intersection", commonMasses)
        #print('dice', dice_coefficient(pubchem_masses, moel_masses))
        #print('overlap', overlap_coefficient(pubchem_masses, moel_masses))
        if len(moelSpectrum_df) > 0:
            rulesActiveHere = moelSpectrum_df[
                moelSpectrum_df["mass"].apply(
                    lambda m: any(abs(m - cm) <= 1.0 for cm in commonMasses)
                )
            ]["rules"]
            
            for rule_group in rulesActiveHere:
                allActiveRules.update(rule_group)

print("allUsedRules", allUsedRules_dict)
print("allActiveRules", allActiveRules)
print("unusedRules", set(allUsedRules_dict.keys()) - allActiveRules)







#printGrammar()
#dg.print()