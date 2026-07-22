"""
Fragmentation and ionization rules for mass spectrometry.
"""

# Import specific rule collections (not wildcard)
from .benzylAllyl_ringGeneral import (
    benzylAllyl_ionizaton,
    benzylAllyl_fragmentation,
)
from .dehydration import dehydration_all
from .deprotonation import deProtonation_all, ei_molecular_ion, heteroatom_ionization
from .IMS_bookCover import (
    IMS_cover_fragmentation,
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

ionization = []
ionization.append(ei_molecular_ion)
ionization.extend(heteroatom_ionization)   # O/N/S/... n-electron ionization; see deprotonation.py
ionization.extend(benzylAllyl_ionizaton)
ionization.extend(wiki_ionization)
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
    "heteroatom_ionization",
    "IMS_cover_fragmentation",
    "IMS_chap4_examples",
    "IMS_chap8_examples",
    "wiki_ionization",
    "wiki_fragmentation",
    "rearrangements",
    "aromatic_ring_loss_fragmentation",
]
