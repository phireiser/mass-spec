include("rules.py")
include("mols.py")
include("predicates.py")

def printGrammar():
        post.summarySection("Molecule(s)")
        p = GraphPrinter()
        p.setMolDefault()
        #p.withIndex = True
        for m in inputGraphs:
                m.print(p)

        post.summarySection("Rule(s)")
        p = GraphPrinter()
        p.setReactionDefault()
        p.withIndex = True
        for r in inputRules:
                r.print(p)



printGrammar()

ionization = [benzylAllyl_ionizaton]
fragmentation = [benzylAllyl_fragmentation]

#universe = [butanl]
universe = [toluene]
#universe = [butylbenzene]


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

ls = LabelSettings(LabelType.Term, LabelRelation.Unification) # switch to term rewite
dg = DG(graphDatabase=inputGraphs, labelSettings=ls)
#dg = DG(graphDatabase=inputGraphs)

with dg.build() as b:
    b.execute(strategy)
dg.print()
