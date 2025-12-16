"""
Deprecated multi-purpose utilities module.

This module previously mixed multiple concerns (inspection, conversions,
masking, and IO). To adhere to the Single Responsibility Principle, the
implementations were moved to dedicated modules in the `utils` subpackage:

- utils.inspection
- utils.conversions
- utils.masking
- utils.io_utils

All names are re-exported here for backward compatibility. Prefer importing
from the dedicated modules going forward.
"""

from __future__ import annotations

import warnings

from .utils.conversions import (
    spectra_to_tensor,
    build_fragment_catalog,
    clean_spectra_tensor,
)
from .utils.masking import (
    frags_to_mask,
    frags_to_soft_mask,
    peaks_to_mask_batch,
)
from .utils.inspection import inspect_hg
from .utils.io_utils import read_mols_csv

_warned = False

def _warn_once() -> None:
    global _warned
    if not _warned:
        warnings.warn(
            "mass_spec_modeling.machine_learning.utils_mod is deprecated. "
            "Use submodules under mass_spec_modeling.machine_learning.utils.* instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        _warned = True

# Trigger a one-time deprecation warning on import
_warn_once()
