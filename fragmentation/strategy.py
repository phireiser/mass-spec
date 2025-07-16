include("predicates.py")
import mod

def makeStrategy(
	universe: List[mod.Graph], 
	ionization: List[mod.Rule], 
	fragmentation: List[mod.Rule]
	) -> mod.DGStrat:

#TODO we should not need this ckeck
#	mass = None
#	try:
#		mass = graphFromTerm(universe[0]).exactMass
#	except mod.libpymod.LogicError: # Can not get exact mass of a non-molecule. 
#		mass = None

	mass = graphFromTerm(universe[0]).exactMass

	strategy = (
			addSubset(universe)
		>> 	subGroup(repeat[1](ionization))
		>> 	chargeBound(
				amuBound(
					subGroup(
						repeat[5](fragmentation)
					),
					minimum = 10, #TODO Research what is the actual pupchem-data minimum
					maximum = mass if mass is not None else 100 #TODO also here: we should not need this ckeck(if)
				)
			)
	)
	return strategy