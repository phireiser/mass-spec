"""
Utilities for the fragmenter project.

This package is a thin facade: each submodule declares its own ``__all__``
(its public surface) and is re-exported here. The package ``__all__`` is
aggregated automatically, so adding a public name only requires updating the
owning submodule's ``__all__`` -- no edit here.

Re-export happens lazily (PEP 562): the submodules are only imported on the
first attribute access, not when this package is imported. This keeps
``mod``-free subpackages (e.g. ``analysis.feasibility``) importable outside
the container, where ``mod`` does not exist.
"""

import importlib

# Submodules whose public API (their own ``__all__``) is exposed at package
# level. Internal helpers (e.g. element_sets, analysis.metrics,
# analysis.pubchem_client) are deliberately omitted; import them directly
# where needed.
_PUBLIC_SUBMODULES = (
    "basic_mod",       # Core graph operations
    "constrain",       # Constraint and rule utilities
    "file",            # Persistence
    "spect_jdx",       # Spectrum I/O
    "spect_mol",
    "spect_pubchem",
    "term_transfers",  # Term transfers (mod integration)
    "analysis.printing",   # Printing and visualization
    "compareability",  # Comparison utilities
    "analysis.describe",   # Description utilities
    "rule_extention",  # Rule extensions
    "mapping",
    "traversal",
    "diag",            # Diagnostics
)


def _load_facade() -> list[str]:
    exported: list[str] = []
    for name in _PUBLIC_SUBMODULES:
        module = importlib.import_module(f".{name}", __name__)
        symbols = getattr(module, "__all__", None)
        if symbols is None:
            raise ImportError(
                f"data_generation.utils submodule '{name}' must define __all__"
            )
        for symbol in symbols:
            globals()[symbol] = getattr(module, symbol)
        exported.extend(symbols)
    globals()["__all__"] = exported
    return exported


def __getattr__(name):
    exported = _load_facade()
    if name == "__all__":
        return exported
    try:
        return globals()[name]
    except KeyError:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        ) from None


def __dir__():
    return sorted(set(globals()) | set(_load_facade()))
