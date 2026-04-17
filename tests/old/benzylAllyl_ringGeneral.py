include("../rules/benzylAllyl_ringGeneral.py")
include("../predicates.py")

ionization = [benzylAllyl_ionizaton]
fragmentation = [benzylAllyl_fragmentation]

toluene = smiles("CC1=CC=CC=C1")
butylbenzene = smiles("CCCCC1=CC=CC=C1")

strategy_t = (addSubset(toluene) 
	>> repeat[1](ionization)
	>> chargeBound(
		amuBound(
			repeat[10](fragmentation),
			minimum=10
			),
		minimum=-10
		)
)

strategy_b = (addSubset(butylbenzene) 
	>> repeat[1](ionization)
	>> chargeBound(
		amuBound(
			repeat[10](fragmentation),
			minimum=10
			),
		minimum=-10
		)
)

dg_t = DG(graphDatabase=inputGraphs)
dg_b = DG(graphDatabase=inputGraphs)

with dg_t.build() as b:
    b.execute(strategy_t)

with dg_b.build() as b:
    b.execute(strategy_b)



c2h2 = Graph.fromGMLString(
"""
graph [
	node [ id 0 label "C" ]
	node [ id 1 label "C" ]
	node [ id 2 label "H" ]
	node [ id 3 label "H" ]
	edge [ source 2 target 0 label "-" ]
	edge [ source 3 target 1 label "-" ]
	edge [ source 0 target 1 label "#" ]
]
"""
)

c3h3 = Graph.fromGMLString(
"""
graph [
	node [ id 0 label "C+" ]
	node [ id 1 label "C" ]
	node [ id 2 label "C" ]
	node [ id 3 label "H" ]
	node [ id 4 label "H" ]
	node [ id 5 label "H" ]
	edge [ source 3 target 0 label "-" ]
	edge [ source 4 target 1 label "-" ]
	edge [ source 5 target 2 label "-" ]
	edge [ source 0 target 1 label "-" ]
	edge [ source 1 target 2 label "=" ]
	edge [ source 0 target 2 label "-" ]
]
"""
)

c4h3 = Graph.fromGMLString(
"""
graph [
	node [ id 0 label "C+" ]
	node [ id 1 label "C" ]
	node [ id 2 label "C" ]
	node [ id 3 label "C" ]
	node [ id 4 label "H" ]
	node [ id 5 label "H" ]
	node [ id 6 label "H" ]
	edge [ source 4 target 1 label "-" ]
	edge [ source 5 target 2 label "-" ]
	edge [ source 6 target 3 label "-" ]
	edge [ source 0 target 1 label "=" ]
	edge [ source 1 target 2 label "-" ]
	edge [ source 2 target 3 label "=" ]
	edge [ source 0 target 3 label "-" ]
]
"""
)

c2 = 0
c3 = 0
c4 = 0

for graph in dg_t.createdGraphs:
    c2 += graph.monomorphism(c2h2)
    c3 += graph.monomorphism(c3h3)
    c4 += graph.monomorphism(c4h3)

assertation_t = all([c2, c3, c4])

if (not assertation_t):
    print(c2, c3, c4)
    for graph in dg_t.createdGraphs:
        print(graph.name + " " + graph.getGMLString())
else:
	print('\x1b[6;30;42m' + 'Success!' + '\x1b[0m')
	

assert assertation_t, "benzyl Allyl Test NOT successful with toluene"



c2 = 0
c3 = 0
c4 = 0

for graph in dg_b.createdGraphs:
    c2 += graph.monomorphism(c2h2)
    c3 += graph.monomorphism(c3h3)
    c4 += graph.monomorphism(c4h3)

assertation_b = all([c2, c3, c4])

if (not assertation_b):
    print(c2, c3, c4)
    for graph in dg_b.createdGraphs:
        print(graph.name + " " + graph.getGMLString())
else:
	print('\x1b[6;30;42m' + 'Success!' + '\x1b[0m')
	

assert assertation_b, "benzyl Allyl Test NOT successful with butylbenzene"


