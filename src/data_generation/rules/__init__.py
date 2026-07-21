"""
Fragmentation and ionization rules for mass spectrometry.
"""

# Import specific rule collections (not wildcard)
from .benzylAllyl_ringGeneral import (
    benzylAllyl_ionizaton,
    benzylAllyl_fragmentation,
)
from .dehydration import dehydration_all
from .deprotonation import deProtonation_all, ei_molecular_ion
from .IMS_bookCover import (
    IMS_cover_fragmentation,
    IMS_cover_ionization,
    rearrangements,
)
from .IMS_chap4_examples import IMS_chap4_examples
from .IMS_chap8_examples import IMS_chap8_examples
from .wikipedia import (
    wiki_ionization,
    wiki_fragmentation,
)
from .aromatic_ring_loss import aromatic_ring_loss_fragmentation

# TODO benzofuran forming fission (BFF)
# TODO quinone methide (QM) fission
# (heterocyclic ring fission: partially covered by aromatic_ring_loss HCN/CO channels)

# KNOWN GAP -- heteroatom ionization.
# The general ionization rule is ``ei_molecular_ion``, "[C]1 >> [C+.]1": it ionizes CARBON
# and nothing else. In real EI the most weakly held electron is a heteroatom n-electron, so
# O/N/S ionization is the norm, and the book's whole Chapter 4 ("reaction initiation at
# radical or charge sites") is built on it. Consequently EVERY rule whose left side needs an
# ionized heteroatom -- hTransition_saturated_1/3/4, hTransition_unsaturated, the ester
# McLafferty pair -- has no substrate unless some other rule happens to walk the charge onto
# a heteroatom first. Only two narrow in-context ionizations exist (``ml_ionization`` and
# ``esterMcLafferty_ionization``).
#
# The general fix is one rule, "[_A]1 >> [_A+.]1 §Y1". Measured on ethyl acetate it takes the
# DG from 14 to 29 edges and recovers m/z 43 (the real base peak), 60 and 29, none of which
# were reachable before. It is NOT enabled here because it widens every DG in the corpus and
# this pipeline's known failure mode is forward-pass memory blow-up -- it needs the same
# measure-then-ship treatment the bimolecular re-authoring got.
ionization = []
ionization.append(ei_molecular_ion)
ionization.extend(benzylAllyl_ionizaton)
ionization.extend(wiki_ionization)
ionization.extend(IMS_cover_ionization)
ionization.extend(deProtonation_all)

fragmentation = []
fragmentation.extend(benzylAllyl_fragmentation)
# fragmentation.extend(deProtonation_all) # hardly probable
fragmentation.extend(dehydration_all)  # intramolecular replacement for the bimolecular IMS_4_28_1
fragmentation.extend(IMS_cover_fragmentation)
fragmentation.extend(IMS_chap4_examples)
fragmentation.extend(IMS_chap8_examples)
fragmentation.extend(wiki_fragmentation)
fragmentation.extend(aromatic_ring_loss_fragmentation)

__all__ = [
    "ionization",
    "fragmentation",
    # Individual rule collections
    "benzylAllyl_ionizaton",
    "benzylAllyl_fragmentation",
    "dehydration_all",
    "deProtonation_all",
    "ei_molecular_ion",
    "IMS_cover_fragmentation",
    "IMS_cover_ionization",
    "IMS_chap4_examples",
    "IMS_chap8_examples",
    "wiki_ionization",
    "wiki_fragmentation",
    "rearrangements",
    "aromatic_ring_loss_fragmentation",
]
