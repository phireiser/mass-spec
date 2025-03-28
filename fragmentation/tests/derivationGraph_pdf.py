include("../rules.py")
include("../mols.py")
include("../predicates.py")
include("../strategy.py")

macLafferty.print()

fragmentation = [ml_rearrRule3, ml_rearrRule2, ml_rearrRule1]
ionization = [ml_hRebind]
oxidation = [ml_ionization]

ionization = [benzylAllyl_ionizaton, dielsAdler_ionization, mcLafferty_ionization]
fragmentation = [benzylAllyl_fragmentation, dielsAdler_fragmentation, mcLafferty_fragmenation, alpha_fragmentation, deProtonation_all]

universe = [toluene]

printGrammar()

#strategy = (addSubset(universe) 
#	>> repeat[1](oxidation)
#	>> rightPredicate[
#		lambda d: chargeBound(d, minimum=-10)
#	](repeat[10](ionization))
#	>> rightPredicate[
#		lambda d: amuBound(d, minimum=10)
#	](repeat[10](fragmentation))
#)

strategy = makeStrategy(universe, ionization, fragmentation)

ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
dg = DG(graphDatabase=inputGraphs, labelSettings=ls)

with dg.build() as b:
    b.execute(strategy)
dg.print()

print("The number of hyperedges in the derivation graph.", dg.numEdges)
