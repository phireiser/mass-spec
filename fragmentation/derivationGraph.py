include("rules.py")
include("predicates.py")

ionization = [benzylAllyl_ionizaton, dielsAdler_ionization, mcLafferty_ionization]
fragmentation = [benzylAllyl_fragmentation, dielsAdler_fragmentation, mcLafferty_fragmenation, alpha_fragmentation,]

strategy = (addSubset(universe) 
	>> repeat[1](ionization)
	>> chargeBound(
		amuBound(
			repeat[10](fragmentation), 
			minimum=10
			),
		minimum=-10
		)
)

#ls = LabelSettings(LabelType.Term, LabelRelation.Unification) # switch to term rewite
#dg = DG(graphDatabase=inputGraphs, labelSettings=ls)
dg = DG(graphDatabase=[universe])

with dg.build() as b:
    b.execute(strategy)