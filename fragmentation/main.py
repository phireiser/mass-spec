import pandas as pd
from pprint import pprint

#include("tests/benzylAllyl_unified.py")

include("mols.py")
include("commons.py")
include("strategy.py")
include("rules.py")

 # only create rules for occuring hetroAtoms
occuring_hetroAtoms = set()
for m in common_ei_molecules:
    for ha in heteroAtoms:
        if m.vLabelCount(ha) > 0:
            occuring_hetroAtoms.add(ha)
heteroAtoms = occuring_hetroAtoms


ionization = [
    benzylAllyl_ionizaton, 
    wiki_ionization,
]
ionization = flatten_list(ionization)

fragmentation = [
    #alpha_fragmentation,
    benzylAllyl_fragmentation,
    cover_fragmentation,
    deProtonation_all,
    IMS_examples,
    #inductive_fragmentation,
    #mcLafferty_fragmenation,
    rearrangements,
    #retroDielsAdler_fragmentation, 
    wiki_fragmentation,
]
fragmentation = flatten_list(fragmentation)

for rulelist in fragmentation + ionization:
    e = rulelist
    #print(e)

allActiveRules = set()

for m in common_ei_molecules: #[linolenicAcid]:
    print("\n")
    print("mol spectrum of", m.name)
    strategy = makeStrategy(universe=[m], ionization=ionization, fragmentation=fragmentation)
    ls = LabelSettings(LabelType.Term, LabelRelation.Unification) # switch to term rewite
    dg = DG(graphDatabase=[m], labelSettings=ls)
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

rules_df = (
    pd.DataFrame(
        [(r.id, r.name) for r in inputRules],  # rows: (id, name)
        columns=["id", "name"],
    )
    .drop_duplicates("id")        # if the two lists could overlap
    .assign(active=False)
    .set_index("id")
)

rules_df.loc[rules_df.index.isin(allActiveRules), "active"] = True

rules_df = rules_df[[col for col in rules_df.columns if col != "name"] + ["name"]]

with pd.option_context(
    'display.max_rows', None,
    'display.max_columns', None,
    'display.width', None,
    'display.max_colwidth', None
):
    print(rules_df)





#printGrammar(inGraphs = common_ei_molecules, inRules = ionization + fragmentation)
#dg.print()

#printRules(ionization + fragmentation)
