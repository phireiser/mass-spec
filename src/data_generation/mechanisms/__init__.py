"""
Mechanism-derived fragmentation rules -- an alternative to
:mod:`src.data_generation.rules`, compiled from the curated corpus in
``data/mechanisms/records`` into ``generated_rules.py`` (a plain, static
``mod.Rule.fromDFS(...)`` module in the same style as the hand-authored files
in ``src/data_generation/rules`` -- see ``write_generated_rules.py`` for how
it is produced, and ``dfs_writer.py`` for the SMIRKS->DFS conversion itself).

SCOPE AND LIMITATIONS -- read before using ``--rule-source mechanisms``
(``src/data_generation/main.py``):

* Each rule is the FULL, CONCRETE molecule/fragment graph from one curated
  book example, not a generalized template with wildcard placeholders like
  the hand-authored ``src/data_generation/rules`` library (which uses ``_A``
  -style placeholders and ``§``-extensions). Because mod matches a rule's
  left graph by SUBGRAPH embedding, a rule still fires on any host molecule
  that happens to contain that exact concrete substructure -- so it is not
  useless outside the literal example molecule -- but it will not generalize
  the way an ``_A``-placeholder hand rule does. This mirrors how
  ``rules/wikipedia.py``'s already-concrete, placeholder-free rules behave in
  production, not a new code path.

  This is the DEFAULT, not the only option: ``write_generated_rules.py
  --context-radius N`` prunes each rule to the atoms its rewrite actually
  touches plus an ``N``-bond shell of context, and
  ``--no-spectator-hydrogens`` stops pinning every matched atom to an exact
  substitution pattern, while ``--placeholder-context`` stops the surviving
  shell positions naming the element the book drew there, writing them as
  ``[_A]`` like the hand-authored rules. Together they turn one book example
  into the reaction class it illustrates -- at the cost of matching (and so enumerating) far
  more, which is the trade-off ``generalize.py`` documents. Whichever way
  ``generated_rules.py`` was written, its module docstring records the flags
  that produced it.
* Only FRAGMENTATION rules are produced. The curated corpus documents
  already-ionized mechanism steps (the book starts from M+*, not a neutral
  molecule), so there is no generic "ionize any molecule" step to compile;
  ``ionization`` is intentionally left for the caller to source from the
  legacy library either way (``main.py --rule-source mechanisms`` still uses
  ``src.data_generation.rules.ionization``).
* Not every curated step converts -- see ``build_rules.iter_conversions``'s
  ``SkippedStep`` entries for *why* a given step was skipped. Regenerate with
  ``python -m src.data_generation.mechanisms.write_generated_rules`` to see
  the full conversion/skip report.
* ``generated_rules.py`` calls ``mod.Rule.fromDFS`` at MODULE-WRITE time (not
  at import time here), same requirement as ``src.data_generation.rules``, so
  it must be (re)generated inside the project container. This package's own
  import is otherwise lightweight -- it just imports the already-written
  rules, it does not re-derive them from JSON+RDKit+mod every run.
"""
from .dfs_writer import MechanismConversionError, reaction_dfs_string
from .generalize import keep_set, prune_graph, reacting_core

ionization = []


_BUILD_RULES_EXPORTS = frozenset(
    {"ConvertedStep", "SkippedStep", "build_mechanism_rules", "iter_conversions"}
)


def __getattr__(name: str):
    # Lazy (PEP 562), second reason: ``build_rules`` imports ``mod``, which only
    # exists inside the project container. Importing it eagerly here would make
    # this package -- and therefore ``dfs_writer``/``generalize``, which need
    # only RDKit -- unimportable outside it, including for
    # ``src/tests/unit_test_mechanisms_dfs_writer.py``, whose whole point is
    # that it runs either side of the container boundary.
    if name in _BUILD_RULES_EXPORTS:
        from . import build_rules
        return getattr(build_rules, name)

    # Lazy (PEP 562): ``generated_rules.py`` is written BY
    # ``write_generated_rules.py``, a submodule of this same package, so
    # importing it eagerly here would make running that writer for the first
    # time impossible (importing any submodule runs this __init__ first).
    # Only actually asking for ``fragmentation`` needs the generated file to
    # already exist.
    if name == "fragmentation":
        try:
            from .generated_rules import fragmentation
        except ImportError as exc:
            raise ImportError(
                "src/data_generation/mechanisms/generated_rules.py does not exist "
                "yet. Generate it (inside the project container, where `mod` is "
                "available) with:\n\n"
                "    python -m src.data_generation.mechanisms.write_generated_rules\n"
            ) from exc
        return fragmentation
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "fragmentation",
    "keep_set",
    "prune_graph",
    "reacting_core",
    "ionization",
    "build_mechanism_rules",
    "iter_conversions",
    "ConvertedStep",
    "SkippedStep",
    "reaction_dfs_string",
    "MechanismConversionError",
]
