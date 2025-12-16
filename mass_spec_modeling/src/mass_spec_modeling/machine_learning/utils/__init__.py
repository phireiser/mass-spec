"""Utilities subpackage for machine_learning.

Modules:
- conversions: spectra and catalog tensor utilities
- masking: fragment-to-catalog matching utilities
- inspection: tensor/hypergraph inspectors
- io_utils: lightweight IO helpers

Prefer importing from these modules directly. The legacy `utils_mod` re-exports
for backward compatibility but is deprecated.
"""

from .conversions import spectra_to_tensor, build_fragment_catalog, clean_spectra_tensor
from .masking import frags_to_mask, frags_to_soft_mask, peaks_to_mask_batch
from .inspection import inspect_hg
from .io_utils import read_mols_csv
