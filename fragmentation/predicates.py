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


def subGroup(strategy):
	def predicate(derivation):
		generalization_extention = ""
		try:
			generalization_extention = derivation.rule.name.split("§")[1]
		except:
			pass

		# if any extention
		if generalization_extention:
			alkylStructures = re.findall(r'R(\d+)', generalization_extention)
			hetroStructures = re.findall(r'Y(\d+)', generalization_extention)
			saturatedStructures = re.findall(r'S(\d+)-(\d+)', generalization_extention)
			
			# make it 0 based
			alkylStructures = [int(x) - 1 for x in alkylStructures]
			hetroStructures = [int(x) - 1 for x in hetroStructures]
			saturatedStructures = [(int(x[0])-1, int(x[1])-1)  for x in saturatedStructures]

			match = getRule2MoleculeMap(derivation = derivation, graphs = dg.graphDatabase, labelSettings = dg.labelSettings)
			if match:
				alkylPosInGraph = [match[vertexById(match.domain, x)] for x in alkylStructures]
				saturatedPosInGraph = [
					(match[vertexById(match.domain, x[0])], match[vertexById(match.domain, x[1])]) 
					for x in saturatedStructures
					]
				hetroPosInGraph = [match[vertexById(match.domain, x)] for x in hetroStructures]
		
				hetro_bool = True
				alkyl_bool = True
				sat_bool = True

				if saturatedPosInGraph:
					sat_bool = saturatedPath(
						graph = derivation.left,
						start_vertex = saturatedPosInGraph[0][0],
						end_vertex = saturatedPosInGraph[0][1], 
						allowed_labels = alk_nes_lables,
						match = match
						) #TODO could contain multiple matches

				print("satbool", sat_bool)
				if alkylPosInGraph:
					alkyl_bool = False
					neighbor_labels, _ = collect_bfs(
						graphs = derivation.left, 
						start_vertices = alkylPosInGraph, 
						match = match
					)
					#print("ngi", derivation.rule.name, neighbor_labels)
					if len(set(neighbor_labels)) > 0 & set(neighbor_labels).issubset(set(alk_nes_lables)):
						alkyl_bool = True


				if hetroPosInGraph:
					hetro_bool = False
					neighbor_labels, _ = collect_bfs(
						graphs = derivation.left, 
						start_vertices = hetroPosInGraph, 
						match = match
					)
					diff = set(neighbor_labels) - set(alk_nes_lables)
					#if len(neighbor_labels) > 0:
						#print("neighb", neighbor_labels) 
						#print("hetro diff", diff)
					if len(diff) <= 1: 
						# not only hetro atoms strictly 
						# as the defnition says but, also carbon atoms
						# as McLafferty book is using them as well
						hetro_bool = True
				print("bool", derivation.rule.name, sat_bool & alkyl_bool & hetro_bool)
				return sat_bool & alkyl_bool & hetro_bool
		return True # if there is no rule extention 

	return rightPredicate[predicate](strategy)

