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




ionization = [benzylAllyl_ionizaton, dielsAdler_ionization, mcLafferty_ionization]
fragmentation = [benzylAllyl_fragmentation, dielsAdler_fragmentation, mcLafferty_fragmenation, alpha_fragmentation,]

#universe = [butanl]
#universe = [toluene]
#universe = [butylbenzene]
#universe = [phenylalanine]
universe = [tyrosine]

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
dg = DG(graphDatabase=universe)

with dg.build() as b:
    b.execute(strategy)

#printGrammar()
#dg.print()

spectra = []
for graph in dg.createdGraphs:
        if graph.isMolecule:
                if '+' in graph.getGMLString():
                        found = False
                        for i,(mass, occurence) in enumerate(spectra):
                                if abs(mass - graph.exactMass) < 1e-3:
                                        spectra[i] = (graph.exactMass, occurence + 1)
                                        found = True
                                        break
                        if not found:            
                                spectra.append((graph.exactMass,1))

print(spectra)