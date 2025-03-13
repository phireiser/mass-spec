def amuBound(derivations, minimum=50, maximum=500):
	def predicate(derivations):
		masses = list()
		for g in derivations.right:
			if g.isMolecule:
				masses.append(g.exactMass)
		r =  any([(mass > minimum) and (mass < maximum) for mass in masses])
		return r
	return rightPredicate[predicate](derivations)

#def chargeBound(derivations, minimum=0, maximum=3):
#	charges = list()
#	for g in derivations.right:
#		if g.isMolecule:
#			charge = 0
#			charge += g.smiles.count('+')
#			charge -= g.smiles.count('-')
#			charges.append(charge)
#	r = any([((charge > minimum) and (charge < maximum)) for charge in charges])
#	return rightPredicate[lambda d: r]


def chargeBound(derivations, minimum=0, maximum=3):
    def predicate(d):
        for g in d.right:
            if g.isMolecule:
                charge = g.smiles.count('+') - g.smiles.count('-')
                if minimum < charge < maximum:
                    return True
        return False

    return rightPredicate[predicate](derivations)


# OPTIMIZATION: (potential) append constraint
def allylGroup(derivations):
	allyl_label = ['C', 'H']
	ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
	def predicate(d):
			for g in d.right:
				match_found = False
				for subgraph in allyl_label:
					if subgraph.monomorphism(g, labelSettings=ls) > 0:
						match_found = True
						break  # found match
				
				if not match_found:
					return False  # not valid 
			
			return True  # at least one match
	return rightPredicate[predicate]
