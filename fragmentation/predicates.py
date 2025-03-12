def amuBound(derivations, minimum=50, maximum=500):
	masses = list()
	for g in derivations.right:
		if g.isMolecule:
			masses.append(g.exactMass)
	r =  any([(mass > minimum) and (mass < maximum) for mass in masses])
	return r

def chargeBound(derivations, minimum=0, maximum=3):
	charges = list()
	for g in derivations.right:
		if g.isMolecule:
			charge = 0
			charge += g.smiles.count('+')
			charge -= g.smiles.count('-')
			charges.append(charge)
	r = any([((charge > minimum) and (charge < maximum)) for charge in charges])
	return r


def allylGroup(derivations):
	for g in derivations.right:
		