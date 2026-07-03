"""Analysis helpers: descriptive statistics, printing, spectrum metrics and
PubChem lookups, plus the feasibility (ceiling / cost) subpackage.

Keep this ``__init__`` free of imports: ``feasibility`` and its unit tests
must stay importable outside the container (no ``mod``, no scientific stack),
and any import here would run for every submodule import. Import the
submodules directly, e.g. ``from src.data_generation.analysis import printing``.
"""
