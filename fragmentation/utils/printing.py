from typing import List
import mod

def print_rules(in_rules: List[mod.Rule]) -> None:
    """
    prints rules in latex in post processing
    """
    post.summarySection("Rule(s)")
    p = GraphPrinter()
    p.setReactionDefault()
    p.withIndex = True
    in_rules = flatten_list(in_rules)
    for r in in_rules:
        r.print(p)


def print_graphs(
    in_graphs: List[mod.Graph]
    ) -> None:
    """
    print graphs in latex in post processing
    """
    post.summarySection("Molecule(s)")
    p = GraphPrinter()
    p.setMolDefault()
    #p.withIndex = True
    for m in in_graphs:
        m.print(p)


def print_grammar(
    in_graphs: List[mod.Graph],
    in_rules: List[mod.Rule],
    ) -> None:

    """
    prints graphs and rules in latex in post processing
    """

    print_graphs(in_graphs)
    print_rules(in_rules)
