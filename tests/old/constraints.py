# add term constraint to rule defined via DFS notation
\

# rule in DFS notation with term variables _X, _Y, _Z
r1 = Rule.fromDFS("[C]1#[N]2.[H]3[_X]4{_Z}[_Y]5>>[H]3[N]2=[C]1[_X]4{_Z}[_Y]5")

# constraint for term variables
r1const = """
constrainLabelAny [
label "Nuc(_X,_Y,_Z)"
labels [ label "Nuc(C,N,#)" label "Nuc(S,C,-)" label "Nuc(N,H,-)" ]
]"""

# add term constraint to rule
r1 = add_constraints(r1, r1const)

print(r1.getGMLString())

# TODO no real test just printing
