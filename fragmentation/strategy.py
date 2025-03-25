#from rules import *
#from predicates import *

include("predicates.py")

def makeStrategy(universe, ionization, fragmentation):

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
	return strategy