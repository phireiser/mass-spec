import mod

# Aromatic ring-opening channels for the radical cation.
#
# These fire on the inert aromatic ring (matching ":" -> e(ar) bonds) and eject a
# small closed-shell neutral, opening the ring. They restore the bare-aromatic
# fragmentation that the old Kekulé ring rules used to provide -- once aromatic
# rings are protected as e(ar), an unsubstituted ring (benzene, naphthalene,
# pyridine, ...) otherwise has no ring-opening pathway and fragments only to M+..
#
# The ejected neutral is closed-shell (C2H2 / HCN / CO), so it carries no charge or
# radical: the charge+radical stay on the retained fragment (a radical cation),
# reproducing the characteristic even-electron neutral losses of EI aromatic
# spectra. A neutral pattern atom [C] cannot match the charged [C+.] under term
# specialisation, so the ejected unit is always taken from the neutral part of the
# ring and the charge is retained by construction.
#
# Each channel was validated by NIST-reference spectral overlap (Dice roughly
# doubled on a representative molecule, and the characteristic peak appears):
#   C2H2  benzene m/z 52, naphthalene 128->102->76   (Dice 0.18 -> 0.36 naphthalene)
#   HCN   pyridine m/z 52                             (Dice 0.14 -> 0.32)
#   CO    phenol m/z 66                               (Dice 0.24 -> 0.45)
# (partially addresses the heterocyclic-ring-fission TODO in rules/__init__.py)


# Loss of acetylene: match 4 consecutive aromatic C-H, eject the middle two as
# HC#CH, opening the ring. Iterates (benzene 78->52, naphthalene 128->102->76->...).
aromatic_C2H2_loss = mod.Rule.fromDFS(
    s =
    "[C]1:[C]2([H]3):[C]4([H]5):[C]6"
    ">>"
    "[C]1" "." "[C]2([H]3){#}[C]4([H]5)" "." "[C]6",
    name = "aromatic C2H2 loss"
)

# Loss of HCN from N-heteroaromatics: eject an aromatic N with an adjacent C-H as
# H-C#N (pyridine 79->52; quinoline, pyrimidine, azines).
aromatic_HCN_loss = mod.Rule.fromDFS(
    s =
    "[C]1:[N]2:[C]3([H]4):[C]5"
    ">>"
    "[C]1" "." "[N]2{#}[C]3([H]4)" "." "[C]5",
    name = "aromatic HCN loss"
)

# Loss of CO from aryl-O compounds with ring contraction: the ipso carbon (no H,
# bears -O-) and its O leave as C#O, the two ring neighbours bond (6->5 ring
# contraction) and the -OH hydrogen migrates onto the ring (phenol 94->66).
aryl_CO_loss = mod.Rule.fromDFS(
    s =
    "[C]2:[C]1(:[C]6)[O]7[H]8"
    ">>"
    "[C]2([H]8):[C]6" "." "[C]1{#}[O]7",
    name = "aryl CO loss (ring contraction)"
)


# Five-membered heteroaromatics (long tail): eject the ring heteroatom X with an
# adjacent ring C-H as H-C=X, opening the ring. Furan -> formyl (H-C=O) leaving
# C3H3+ (m/z 39); thiophene -> thioformyl (H-C=S) leaving C3H3+ (m/z 39). These
# fire only where an aromatic O/S sits in a ring next to an aromatic C-H, so they
# are self-limiting to O-/S-heteroaromatics. NIST-validated: furan 68->39
# (Dice 0.14->0.26), thiophene 84->39. (Pyrrole's analogous HCN loss is not shipped:
# the store has no pyrrole reference to validate against.)
furan_CHO_loss = mod.Rule.fromDFS(
    s =
    "[C]3:[C]2([H]4):[O]1:[C]5"
    ">>"
    "[C]3" "." "[C]2([H]4){=}[O]1" "." "[C]5",
    name = "furan CHO loss"
)

thiophene_HCS_loss = mod.Rule.fromDFS(
    s =
    "[C]3:[C]2([H]4):[S]1:[C]5"
    ">>"
    "[C]3" "." "[C]2([H]4){=}[S]1" "." "[C]5",
    name = "thiophene HCS loss"
)


aromatic_ring_loss_fragmentation = [
    aromatic_C2H2_loss,
    aromatic_HCN_loss,
    aryl_CO_loss,
    furan_CHO_loss,
    thiophene_HCS_loss,
]
