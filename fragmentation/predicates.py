def amuBound(strategy, minimum=50, maximum=500):
	def predicate(derivations):
		masses = list()
		for g in derivations.right:
			if g.isMolecule:
				masses.append(g.exactMass)
		r =  any([(mass > minimum) and (mass < maximum) for mass in masses])
		return r
	return rightPredicate[predicate](strategy)

def chargeBound(strategy, minimum=0, maximum=1):
    def predicate(d):
        for g in d.right:
            if g.isMolecule:
                charge = g.smiles.count('+') - g.smiles.count('-')
                if minimum <= charge <= maximum:
                    return True
        return False

    return rightPredicate[predicate](strategy)


# OPTIMIZATION: (potential) append constraint
def allylGroup(strategy):
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
	return rightPredicate[predicate](strategy)

def subGroup(strategy):
	heteroAtoms = [
    	"He","Li","Be","B","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca",
    	"Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb",
    	"Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe",
    	"Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
    	"Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra",
    	"Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es"
	]

	ls = LabelSettings(LabelType.Term, LabelRelation.Unification)

	# how can I access the rule name?

