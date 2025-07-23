from typing import List
import mod

def printRules(inRules: List[mod.Rule]) -> None:
    post.summarySection("Rule(s)")
    p = GraphPrinter()
    p.setReactionDefault()
    p.withIndex = True
    inRules = flatten_list(inRules)
    for r in inRules:
            r.print(p)


def printGraphs(
    inGraphs: List[mod.Graph]
    ) -> None:
    post.summarySection("Molecule(s)")
    p = GraphPrinter()
    p.setMolDefault()
    #p.withIndex = True
    for m in inGraphs:
            m.print(p)


def printGrammar(
    inGraphs: List[mod.Graph],
    inRules: List[mod.Rule],
    ) -> None:
    printGraphs(inGraphs)
    printRules(inRules)
