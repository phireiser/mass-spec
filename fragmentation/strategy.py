#from rules import *
#from predicates import *

include("predicates.py")

def makeStrategy(universe, ionization, fragmentation):

	strategy = (addSubset(universe) 
		>> repeat[1](ionization)
		>> chargeBound(
			amuBound(
				repeat[5](fragmentation), 
				minimum = 35, #TODO Reaserch what is the actual pupchem-data minimum
				maximum = universe[0].exactMass
				)
			)
	)
	return strategy