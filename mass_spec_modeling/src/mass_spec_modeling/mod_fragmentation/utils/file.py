"""
dump & load the full (including ruleDB & graphDB) derivation graph
"""

import pickle
from typing import List
import mod

def dump_derivation_graph(
    dg: mod.DG,
    rule_list: List[mod.Rule],
    name: str,
    path: str = "./dump/"
) -> None:

    """dump DG"""

    dg.dump(path + name + ".dmp")

    graph_database = []
    for obj in dg.graphDatabase:
        graph_database.append(obj.getGMLString())

    rule_database = []
    for obj in rule_list:
        rule_database.append(obj.getGMLString())

    with open(path + name + ".pkl", 'wb') as f:
        pickle.dump((graph_database, rule_database), f)


def load_derivation_graph(name: str, path: str = "./dump/") -> mod.DG:
    """load DG"""

    with open(path + name + ".pkl", 'rb') as f:
        (graph_list, rule_list) = pickle.load(f)

    graph_database = []
    for gml in graph_list:
        graph_database.append(mod.graphGMLString(gml))

    rule_database = []
    for gml in rule_list:
        rule_database.append(mod.ruleGMLString(gml))

    dg = mod.DG.load(
        graphDatabase = graph_database,
        ruleDatabase = rule_database,
        f = path + name + ".dmp"
    )

    return dg, rule_database
