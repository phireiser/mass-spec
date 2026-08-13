"""
Get spectrum from a MOD derivation graph.
"""
import pickle
import re
from pathlib import Path
from typing import Set, List, Tuple
import mod
from . import codec
from .term_transfers import graph_from_term, atom_exact_mass, electron_mass

def get_parent_rules_for_graph(
    derivation_graph: mod.DG,
    search_target_graph: mod.Graph
    ) -> List[int]:
    """
    Get all rule IDs that are used as parents (precursors) of the given product graph.
    """
    parent_rules = []
    visited = set()
    stack = [search_target_graph]

    while stack:
        current_graph = stack.pop()
        # Avoid reprocessing the same graph
        if current_graph in visited:
            continue
        visited.add(current_graph)
        edges = derivation_graph.findVertex(current_graph).inEdges
        for edge in edges:
            for rule in edge.rules:
                parent_rules.append(rule.id)

            for source in edge.sources:
                stack.append(source.graph)

    return parent_rules


def get_spectra_from_mod_derivation_graph(
    derivation_graph: mod.DG
    ) -> List[Tuple[float, int, Set[int]]]:
    """
    Get spectra from a MOD derivation graph.
    """
    spectra = []
    for graph_term in derivation_graph.graphDatabase:  # Note: when loading DG, len(createdGraphs) == 0
        graph = graph_from_term(graph_term)
        if graph.isMolecule:
            if '+' in graph.getGMLString():  # Only charged fragments can be detected
                found = False  # Update spectra list if already occurring
                rules = set(get_parent_rules_for_graph(derivation_graph,graph_term))

                for i, (mass, occurrence, old_rules) in enumerate(spectra):
                    if abs(mass - graph.exactMass) < 1e-2:
                        spectra[i] = (graph.exactMass, occurrence + 1, old_rules.union(rules))
                        found = True
                        break
                if not found:  # Add to spectra list if not occurring
                    spectra.append((graph.exactMass, 1, rules))
        else:
            print(graph.getGMLString())
            raise RuntimeWarning("There are graphs that are not molecules.")
    return spectra


# Term vertex label as written into the dumped GML: ``a(Symbol, charge, radical)``.
_TERM_NODE_RE = re.compile(r'label\s+"a\(\s*([^,\s]+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)"')

# Memoised per symbol; the raise-on-placeholder outcome is cached too, so a dump full of
# placeholder species does not pay mod's graph construction once per occurrence.
_SYMBOL_MASS: "dict[str, float]" = {}


def _atom_mass_cached(symbol: str) -> float:
    """``atom_exact_mass`` with the failure memoised as well as the success."""
    if symbol in _SYMBOL_MASS:
        cached = _SYMBOL_MASS[symbol]
        if cached is None:
            raise ValueError(f"non-element symbol {symbol!r}")
        return cached
    try:
        mass = atom_exact_mass(symbol)
    except Exception:
        _SYMBOL_MASS[symbol] = None
        raise
    _SYMBOL_MASS[symbol] = mass
    return mass


def get_spectra_from_dump(
    name: str,
    path: Path,
    ) -> List[Tuple[float, int, Set[int]]]:
    """Same spectrum as :func:`get_spectra_from_mod_derivation_graph`, without loading the DG.

    ``DefaultDGStore.load`` calls ``mod.Graph.fromGMLString`` on every species, which registers
    each graph in mod's **process-global** database and runs isomorphism checks against
    everything registered so far. That is fine once and quadratic over a batch: scoring the
    Phase-1 decoy set in one process reached 14 GB RSS and slowed from 17 targets/hour to 22
    targets/day before it was killed.

    It is also unnecessary here. The spectrum is a function of the species alone -- the DG's
    edges feed only the per-peak ``rules`` field -- and every species is already in the
    ``.pkl`` as a GML string. So parse that text instead. Returns ``rules`` as an empty set;
    callers needing provenance must still load the DG.

    Semantics are mirrored from the DG version rather than approximated, because two details
    silently change the metric if you get them wrong:

    * **charged means "carries a positive atom", not "net charge >= 1".** The DG version tests
      ``'+' in graph.getGMLString()`` on the *molecule* graph, so a zwitterion with +1 and -1
      is included despite a net of 0. Testing ``net >= 1`` would drop it.
    * **occurrence counts species, not derivations**, and species are pooled at ``1e-2`` on the
      exact mass -- so the grouping tolerance has to match, not just the rounding.

    Species carrying a placeholder (non-element) symbol are skipped, mirroring the
    ``isMolecule`` guard.
    """
    # Streams straight out of the compressed pickle -- still never touches the .dmp, so
    # the global-graph-registry blowup described above stays fixed and peak RSS is
    # unchanged.
    with codec.open_read(Path(path) / (name + ".pkl")) as fh:
        data = pickle.load(fh)
    graph_list = data[1]

    spectra: List[Tuple[float, int, Set[int]]] = []
    for gml in graph_list:
        atoms = _TERM_NODE_RE.findall(gml)
        if not atoms:
            continue
        total, net, positive, concrete = 0.0, 0, False, True
        for symbol, charge, _radical in atoms:
            # atom_exact_mass RAISES on a placeholder symbol (`_A`, wildcards) rather than
            # returning None -- it asks mod to build a one-node graph. Treat that as
            # "not a molecule" and drop the species, mirroring the isMolecule guard.
            try:
                total += _atom_mass_cached(symbol)
            except Exception:  # noqa: BLE001 - a placeholder must not kill the extraction
                concrete = False
            c = int(charge)
            net += c
            if c > 0:
                positive = True
        if not concrete or not positive:
            continue
        exact = total - net * electron_mass()

        for i, (mass, occurrence, rules) in enumerate(spectra):
            if abs(mass - exact) < 1e-2:
                spectra[i] = (exact, occurrence + 1, rules)
                break
        else:
            spectra.append((exact, 1, set()))
    return spectra


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "get_parent_rules_for_graph",
    "get_spectra_from_mod_derivation_graph",
    "get_spectra_from_dump",
]
