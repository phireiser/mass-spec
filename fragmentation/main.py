import pandas as pd
from pprint import pprint

#include("tests/benzylAllyl_unified.py")
include("commons.py")
include("mols.py") # mols before rules
include("rules.py")
include("strategy.py")


allActiveRules = set()


for m in common_ei_mol_term: #small_ei_mol_term: common_ei_mol_term:
    print("\n")
    print("mol spectrum of", m.name)
    strategy = makeStrategy(universe=[m], ionization=ionization_term, fragmentation=fragmentation_term)
    ls = LabelSettings(LabelType.Term, LabelRelation.Unification) # switch to term rewite
    dg = DG(graphDatabase=[m], labelSettings=ls)
    dg.build().execute(strategy)

    pubchemSpectra = getSpectraFromPubChem(graphFromTerm(m).smiles)
    moelSpectrum_dict = getSpectraFromMoelDerivationGraph(dg)
    moelSpectrum_df = pd.DataFrame(moelSpectrum_dict, columns=["mass", "intensity", "rules"])

    dice_max = -1.0
    for pubchemSpectrum in pubchemSpectra:

        pubchem_masses = set([int(x[0]) for x in list(pubchemSpectrum.values())[0]])
        moel_masses = set([int(x[0]) for x in moelSpectrum_dict])

        #print("masses:\t", "pubchem", pubchem_masses, "moel", moel_masses)
        #print("intersection", pubchem_masses & moel_masses)
        #print('dice', dice_coefficient(pubchem_masses, moel_masses))
        #print('overlap', overlap_coefficient(pubchem_masses, moel_masses))

        dice_max = max(dice_max, dice_coefficient(pubchem_masses, moel_masses))

        # collect rules that created matching masses threshold +/- 1
        if len(moelSpectrum_df) > 0:
            rulesActiveHere = moelSpectrum_df[
                moelSpectrum_df["mass"].apply(
                    lambda m: any(abs(m - cm) <= 1.0 for cm in pubchem_masses)
                )
            ]["rules"]
            
            for rule_group in rulesActiveHere:
                allActiveRules.update(rule_group)
    print("dice Maximum", dice_max)

# build a DataFrame of ALL Rules anywhere
rules_df = (
    pd.DataFrame(
        [(r.id, r.name) for r in set(ionization_term + fragmentation_term + inputRules)],  # rows: (id, name)
        columns=["id", "name"],
    )
    .drop_duplicates("id")        # if the two lists could overlap
    .assign(active=False)
    .set_index("id")
)

rules_df.loc[rules_df.index.isin(allActiveRules), "active"] = True

rules_df = rules_df[[col for col in rules_df.columns if col != "name"] + ["name"]]

print("\n\n")

with pd.option_context(
    'display.max_rows', None,
    'display.max_columns', None,
    'display.width', None,
    'display.max_colwidth', None
    ):
    print(rules_df)




#printGrammar(inGraphs = [toluene] #common_ei_molecules
#, inRules = ionization + fragmentation)
#
#dg.print()
#
#printRules(ionization_term + fragmentation_term)
