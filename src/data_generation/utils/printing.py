"""
printing methods for latex
"""

from typing import List
import mod
from mod import post

from .term_transfers import graph_from_term, rule_from_term


def _is_term_graph(g: mod.Graph) -> bool:
    """
    True if ``g`` is still in term mode, i.e. its vertices carry term-bracketed
    labels like ``a(C, 0, 0)`` rather than plain string labels like ``C``.
    Such graphs print as raw term syntax in LaTeX instead of a molecule.
    """
    return any(v.stringLabel.startswith("a(") for v in g.vertices)


def _as_string_graph(g: mod.Graph) -> mod.Graph:
    """Round-trip a term-mode graph back to string mode; pass others through."""
    return graph_from_term(g) if _is_term_graph(g) else g


def _is_term_rule(r: mod.Rule) -> bool:
    """True if rule ``r`` is still in term mode (term-bracketed vertex labels)."""
    return any(
        v.stringLabel.startswith("a(")
        for side in (r.left, r.right)
        for v in side.vertices
    )


def _as_string_rule(r: mod.Rule) -> mod.Rule:
    """Round-trip a term-mode rule back to string mode; pass others through."""
    return rule_from_term(r) if _is_term_rule(r) else r


def print_rules(
    in_rules: List[mod.Rule]
    ) -> None:
    """
    prints rules in latex in post processing
    """
    post.summarySection("Rule(s)")
    p = mod.GraphPrinter()
    p.setReactionDefault()
    p.withIndex = True
    for r in in_rules:
        _as_string_rule(r).print(p)


def print_graphs(
    in_graphs: List[mod.Graph]
    ) -> None:
    """
    print graphs in latex in post processing
    """
    post.summarySection("Molecule(s)")
    p = mod.GraphPrinter()
    p.setMolDefault()
    #p.withIndex = True
    for m in in_graphs:
        _as_string_graph(m).print(p)


def print_grammar(
    in_graphs: List[mod.Graph],
    in_rules: List[mod.Rule]
    ) -> None:
    """
    prints graphs and rules in latex in post processing
    """
    print_graphs(in_graphs)
    print_rules(in_rules)


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "print_rules",
    "print_graphs",
    "print_grammar",
]
