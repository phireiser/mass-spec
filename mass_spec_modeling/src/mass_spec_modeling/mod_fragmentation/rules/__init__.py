"""
Fragmentation and ionization rules for mass spectrometry.
"""

# Import specific rule collections (not wildcard)
from .benzylAllyl_ringGeneral import (
    benzylAllyl_ionizaton,
    benzylAllyl_fragmentation,
)
from .deprotonation import deProtonation_all
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

# TODO heterocyclic ring fission (HRF)
# TODO benzofuran forming fission (BFF)
# TODO quinone methide (QM) fission

# Curated rule collections for common usage
ionization = []
ionization.extend(benzylAllyl_ionizaton)
ionization.extend(wiki_ionization)
ionization.extend(deProtonation_all)

fragmentation = []
fragmentation.extend(benzylAllyl_fragmentation)
# fragmentation.extend(deProtonation_all) # hardly probable
fragmentation.extend(IMS_cover_fragmentation)
fragmentation.extend(IMS_chap4_examples)
fragmentation.extend(IMS_chap8_examples)
fragmentation.extend(wiki_fragmentation)

__all__ = [
    "ionization",
    "fragmentation",
    # Individual rule collections
    "benzylAllyl_ionizaton",
    "benzylAllyl_fragmentation",
    "deProtonation_all",
    "IMS_cover_fragmentation",
    "IMS_chap4_examples",
    "IMS_chap8_examples",
    "wiki_ionization",
    "wiki_fragmentation",
    "rearrangements",
]
