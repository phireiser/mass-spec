include("rules.py")
include("mols.py")
include("predicates.py")

macLafferty.print()



fragmentation = [benzylAllyl_fragmentation]
oxidation = [benzylAllyl_oxidation]

universe = [butanl]




strategy = (addSubset(universe) 
	>> repeat[1](oxidation)
	>> chargeBound(amuBound(repeat[10](fragmentation), minimum=10), minimum=-10)
)

ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
dg = DG(graphDatabase=inputGraphs, labelSettings=ls)

with dg.build() as b:
    b.execute(strategy)
dg.print()
