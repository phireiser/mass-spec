"""
Utilities for the fragmenter project.

This package is a thin facade: each submodule declares its own ``__all__``
(its public surface) and is re-exported here via ``from .module import *``.
The package ``__all__`` is aggregated automatically, so adding a public name
only requires updating the owning submodule's ``__all__`` -- no edit here.
"""

import importlib

# Submodules whose public API (their own ``__all__``) is exposed at package
# level. Internal helpers (e.g. element_sets) are deliberately omitted;
# import them directly where needed. Analysis helpers (printing, describe,
# metrics, pubchem_*) live in ``src.data_generation.analysis``.
_PUBLIC_SUBMODULES = (
    "basic_mod",       # Core graph operations
    "constrain",       # Constraint and rule utilities
    "file",            # Persistence
    "spect_jdx",       # Spectrum I/O
    "dump_naming",     # CAS-first dump stem resolution
    "spect_mol",
    "spect_pubchem",
    "term_transfers",  # Term transfers (mod integration)
    "compareability",  # Comparison utilities
    "rule_extention",  # Rule extensions
    "mapping",
    "traversal",
    "diag",            # Diagnostics
)

__all__: list[str] = []

for _name in _PUBLIC_SUBMODULES:
    _module = importlib.import_module(f".{_name}", __name__)
    _exported = getattr(_module, "__all__", None)
    if _exported is None:
        raise ImportError(
            f"data_generation.utils submodule '{_name}' must define __all__"
        )
    for _symbol in _exported:
        globals()[_symbol] = getattr(_module, _symbol)
    __all__.extend(_exported)

del importlib, _name, _module, _exported, _symbol
