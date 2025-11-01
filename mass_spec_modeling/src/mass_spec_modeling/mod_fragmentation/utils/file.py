"""
dump & load the full (including ruleDB & graphDB) derivation graph
"""

import pickle
from typing import List, Tuple
from pathlib import Path
import mod


def dump_derivation_graph(
    dg: mod.DG,
    rule_list: List[mod.Rule],
    name: str,
    smiles: str,
    true_spectrum: List[Tuple[int, float]],
    path: Path | str = Path("./dump/")
) -> None:
    """
    Dump the derivation graph and minimal databases to files under path.
    Creates two files:
    - <name>.dmp: binary DG dump via mod.DG.dump
    - <name>.pkl: pickle with (smiles, graph_database_gml, rule_database_gml, true_spectrum)
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    dg.dump(str(path / (name + ".dmp")))

    graph_database = []
    for obj in dg.graphDatabase:
        graph_database.append(obj.getGMLString())

    rule_database = []
    for obj in rule_list:
        rule_database.append(obj.getGMLString())

    with open(path / (name + ".pkl"), 'wb') as f:
        pickle.dump((smiles, graph_database, rule_database, true_spectrum), f)


def load_derivation_graph(name: str, path: Path | str = Path("./dump/")) -> Tuple[mod.DG, List[mod.Rule]]:
    """
    Load a derivation graph and its rule database from disk.
    Returns (dg, rule_database) where rule_database is a list of mod.Rule.
    """
    path = Path(path)

    with open(path / (name + ".pkl"), 'rb') as f:
        (_smiles, graph_list, rule_list, _true_spectrum) = pickle.load(f)

    graph_database = []
    for gml in graph_list:
        graph_database.append(mod.Graph.fromGMLString(gml))

    rule_database = []
    for gml in rule_list:
        rule_database.append(mod.Rule.fromGMLString(gml))

    dg = mod.DG.load(
        graphDatabase = graph_database,
        ruleDatabase = rule_database,
        f = str(path / (name + ".dmp"))
    )

    return dg, rule_database
