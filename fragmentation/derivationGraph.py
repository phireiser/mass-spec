include("rules.py")
include("mols.py")
include("predicates.py")

macLafferty.print()



fragmentation = [rearrRule3, rearrRule2, rearrRule1]
ionization = [HrebindRule]
oxidation = [oxidRule]


universe = [butanl]




strategy = (addSubset(universe) 
	>> repeat[1](oxidation)
	>> rightPredicate[
		lambda d: chargeBound(d, minimum=-10)
	](repeat[10](ionization))
	>> rightPredicate[
		lambda d: amuBound(d, minimum=10)
	](repeat[10](fragmentation))
)

ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
dg = DG(graphDatabase=inputGraphs, labelSettings=ls)

with dg.build() as b:
    b.execute(strategy)
dg.print()
