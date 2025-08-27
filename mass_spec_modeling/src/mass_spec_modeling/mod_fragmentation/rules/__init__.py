from ..utils import *

from .benzylAllyl_ringGeneral import *
from .deprotonation import *
from .IMS_bookCover import *
from .IMS_chap4_examples import *
from .IMS_chap8_examples import *
from .wikipedia import *


# TODO heterocyclic ring fission (HRF)
# TODO benzofuran forming fission (BFF)
# TODO quinone methide (QM) fission


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
