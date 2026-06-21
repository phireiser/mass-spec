"""
Derivation graph storage helpers with a small interface for SOLID compliance.
"""
from __future__ import annotations
import pickle
from typing import List, Tuple, Protocol
from pathlib import Path
import mod


class DefaultDGStore:
    def dump(self, dg: mod.DG, rule_list: List[mod.Rule], name: str, smiles: str, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        dg.dump(str(path / (name + ".dmp")))
        graph_database = [obj.getGMLString() for obj in dg.graphDatabase]
        rule_database = [obj.getGMLString() for obj in rule_list]
        with open(path / (name + ".pkl"), 'wb') as f:
            pickle.dump((smiles, graph_database, rule_database), f)

    def load(self, name: str, path: Path) -> mod.DG:
        with open(path / (name + ".pkl"), 'rb') as f:
            data = pickle.load(f)
        if len(data) == 3:
            (_smiles, graph_list, rule_list) = data
        elif len(data) == 4:
            (_smiles, graph_list, rule_list, _true_spectrum) = data
        else:
            raise RuntimeError(f"Failed to load pickle file {path / (name + '.pkl')}: Unexpected data format (length {len(data)})")
        graph_database = [mod.Graph.fromGMLString(gml) for gml in graph_list]
        rule_database = [mod.Rule.fromGMLString(gml) for gml in rule_list]
        dg = mod.DG.load(graphDatabase=graph_database, ruleDatabase=rule_database, f=str(path / (name + ".dmp")))
        return dg


def dump_derivation_graph(dg: mod.DG, rule_list: List[mod.Rule], name: str, smiles: str, path: Path | str = Path("./dump/")) -> None:
    store = DefaultDGStore()
    store.dump(dg, rule_list, name, smiles, Path(path))


def load_derivation_graph(name: str, path: Path | str = Path("./dump/")) -> mod.DG:
    store = DefaultDGStore()
    return store.load(name, Path(path))


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "dump_derivation_graph",
    "load_derivation_graph",
]
