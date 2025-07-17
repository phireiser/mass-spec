include("../rules.py")
#include("../mols.py")
include("../predicates.py")
include("../strategy.py")

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


universe = [
    Graph.fromDFS("[C]1[_A+.]2[H]3([H]4)"),
    Graph.fromDFS("[C]1[N.]2[H]3([H]4)"),
    Graph.fromDFS("[C]1([C]2)[O+]3[H]4([H]5)"),
]

ionization_term = []
for r in ionization:
    ionization_term.append(termFromRule(r))

fragmentation_term = []
for r in fragmentation:
    fragmentation_term.append(termFromRule(r))

universe_term = []
for g in universe:
    universe_term.append(termFromGraph(g))

universe_back = []
for g in universe_term:
    universe_back.append(graphFromTerm(g))



printGrammar()

strategy = makeStrategy(universe_term, ionization_term, fragmentation_term)

ls = LabelSettings(LabelType.Term, LabelRelation.Unification) # switch to term rewite
dg = DG(graphDatabase=universe_term, labelSettings=ls)

with dg.build() as b:
    b.execute(strategy)
dg.print()

print("The number of hyperedges in the derivation graph.", dg.numEdges)
