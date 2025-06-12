import re
import networkx as nx

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


## OPTIMIZATION: (potential) append constraint
#def allylGroup(strategy):
#	allyl_label = ['C', 'H']
#	ls = LabelSettings(LabelType.Term, LabelRelation.Unification)
#	def predicate(d):
#			for g in d.right:
#				match_found = False
#				for subgraph in allyl_label:
#					if subgraph.monomorphism(g, labelSettings=ls) > 0:
#						match_found = True
#						break  # found match
#				
#				if not match_found:
#					return False  # not valid 
#			
#			return True  # at least one match
#	return rightPredicate[predicate](strategy)

def subGroup(strategy):
	heteroAtoms = [
    	"He","Li","Be","B","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca",
    	"Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb",
    	"Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe",
    	"Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
    	"Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra",
    	"Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es"
	]
	
	alk_nes_lables = ["H", "C"] # alkanes (single bond), alkenes(>=1 double bond), alkynes (>=1 tripple bond)

	def predicate(derivation):
		generalization_extention = ""
		try:
			generalization_extention = derivation.rule.name.split("^")[1]
		except:
			pass

		# if any extention
		if generalization_extention:
			#print('.', end='') # is beeing called so many times see slurm job 8298630
			alkylStructures = re.findall(r'R(\d+)', generalization_extention)
			hetroStructures = re.findall(r'Y(\d+)', generalization_extention)
			saturatedStructures = re.findall(r'S(\d+)-(\d+)', generalization_extention)
			
			# make it 0 based
			alkylStructures = [int(x) - 1 for x in alkylStructures]
			hetroStructures = [int(x) - 1 for x in hetroStructures]
			saturatedStructures = [(int(x[0])-1, int(x[1])-1)  for x in saturatedStructures]

			match = getRule2MoleculeMap(derivation = derivation, graphs = dg.graphDatabase)
			if match:
				try:
					alkylPosInRule = [match[vertexById(match.domain, x)] for x in alkylStructures]
				except StopIteration:
					print("structures", alkylStructures)
					print("rule", derivation.rule)
				saturatedPosInRule = [
					(match[vertexById(match.domain, x[0])], match[vertexById(match.domain, x[1])]) 
					for x in saturatedStructures
					]
				hetroPosInRule = [match[vertexById(match.domain, x)] for x in hetroStructures]
		

				hetro_bool = True
				alkyl_bool = True
				sat_bool = True


				if saturatedPosInRule:
					sat_bool = path_no_branches(
						graph = derivation.left,
						start_vertex = saturatedPosInRule[0][0],
						end_vertex = saturatedPosInRule[0][1], 
						allowed_labels = alk_nes_lables,
						match = match
						) #TODO could contain multiple matches


				if alkylPosInRule:
					alkyl_bool = False
					neighbor_labels, _ = collect_bfs(
						graph = derivation.left, 
						start_vertices = alkylPosInRule, 
						match = match
						)
					if set(neighbor_labels).issubset(set(alk_nes_lables)):
						alkyl_bool = True


				if hetroPosInRule:
					hetro_bool = False
					neighbor_labels, _ = collect_bfs(
						graph = derivation.left, 
						start_vertices = hetroPosInRule, 
						match = match
					)
					diff = set(neighbor_labels) - set(alk_nes_lables)
					if len(diff) <= 1: 
						# not only hetro atoms strictly 
						# as the defnition says but, also alkyl atoms
						hetro_bool = True

				return sat_bool & alkyl_bool & hetro_bool
			# enif mapping exist
		# endif extention exists
		return True

	return rightPredicate[predicate](strategy)

