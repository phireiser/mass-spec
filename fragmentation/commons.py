import requests
import json
import warnings
import re
import itertools
import sys
import os
import networkx as nx
import mod

from collections import deque, Counter
from typing import List, Tuple, Iterable, Set, Hashable, Dict, Optional

include("util_netX.py")
include("util_rule_extention.py")
include("util_spect_mol.py")
include("util_spect_PubChem.py")
include("util_term_transfers.py")
include("util_constrain.py")


def dice_coefficient(a, b): # like F1 Socre
    set_a, set_b = set(a), set(b)
    return 2 * len(set_a & set_b) / (len(set_a) + len(set_b))


def overlap_coefficient(a, b):
    set_a, set_b = set(a), set(b)
    res = 0
    try:
        res = len(set_a & set_b) / min(len(set_a), len(set_b))
    except(ZeroDivisionError):
        res = 0.0
    return res


def split_rule_dfs(rule: str) -> Tuple[List[str], List[str]]:
    """
    Split a ruleDFS of the form
        graphs_left >> graphs_right
    into two lists while ignoring dots that are inside any brackets.

    Returns
    -------
    left_graphs  : list[str]
    right_graphs : list[str]
    """
    # separate left & right
    if ">>" not in rule:
        raise ValueError("ruleDFS must contain '>>'")
    left_raw, right_raw = map(str.strip, rule.split(">>", 1))

    # helper: top-level dot splitter using ONE depth counter
    def split_side(side: str) -> List[str]:
        graphs, buf, depth = [], [], 0
        for ch in side:
            if ch in "[({":        # any opening bracket
                depth += 1
            elif ch in "])}":      # any closing bracket
                depth -= 1

            if ch == "." and depth == 0:   # separator only at top level
                graph = "".join(buf).strip()
                if graph:
                    graphs.append(graph)
                buf.clear()
            else:
                buf.append(ch)

        last = "".join(buf).strip()
        if last:
            graphs.append(last)
        return graphs

    return split_side(left_raw), split_side(right_raw)


def flatten_list(nested_list):
    """
    Flattens a nested list into a single list.
    
    :param nested_list: A list which may contain other lists
    :return: A flattened list
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def printRules(inRules):
    post.summarySection("Rule(s)")
    p = GraphPrinter()
    p.setReactionDefault()
    p.withIndex = True
    inRules = flatten_list(inRules)
    for r in inRules:
            r.print(p)


def printGraphs(inGraphs):
    post.summarySection("Molecule(s)")
    p = GraphPrinter()
    p.setMolDefault()
    #p.withIndex = True
    for m in inGraphs:
            m.print(p)


def printGrammar(inGraphs = inputGraphs, inRules = inputRules):
    printGraphs(inGraphs)
    printRules(inRules)


class ComparableVertex:
    def __init__(self, vertex, attrs=("id", "stringLabel")):
        if isinstance(vertex, ComparableVertex):  # unwrap if needed
            vertex = vertex.vertex
        self.vertex = vertex
        self.attrs = (attrs,) if isinstance(attrs, str) else tuple(attrs)

    def __eq__(self, other):
        if isinstance(other, ComparableVertex):
            other_vertex = other.vertex
        elif isinstance(other, mod.Graph.Vertex):
            other_vertex = other
        else:
            return NotImplemented
        return all(getattr(self.vertex, attr) == getattr(other_vertex, attr) for attr in self.attrs)

    def __hash__(self):
        return hash(tuple(getattr(self.vertex, attr) for attr in self.attrs))

    def __repr__(self):
        return f"ComparableVertex({', '.join(f'{a}={getattr(self.vertex, a)}' for a in self.attrs)})"


class ComparableVertexList:
    def __init__(self, vertices, attrs=("id", "stringLabel")):
        self.attrs = (attrs,) if isinstance(attrs, str) else tuple(attrs)
        self._wrapped = [
            ComparableVertex(v.vertex if isinstance(v, ComparableVertex) else v, self.attrs)
            for v in vertices
        ]

    def __contains__(self, vertex):
        return ComparableVertex(vertex, self.attrs) in self._wrapped

    def add(self, vertex):
        wrapped = ComparableVertex(vertex, self.attrs)
        if wrapped not in self._wrapped:
            self._wrapped.append(wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __iter__(self):
        return (cv.vertex for cv in self._wrapped)

    def __getitem__(self, index):
        return self._wrapped[index].vertex

    def __repr__(self):
        return f"ComparableVertexList([\n  " + ",\n  ".join(repr(cv) for cv in self._wrapped) + "\n])"

    def to_raw_list(self):
        return [cv.vertex for cv in self._wrapped]

    def to_wrapped(self):
        return self._wrapped.copy()

    def __eq__(self, other):
        if isinstance(other, ComparableVertexList):
            return self.attrs == other.attrs and set(self._wrapped) == set(other._wrapped)
        elif isinstance(other, ComparableVertex):
            return other in self._wrapped
        elif isinstance(other, mod.Graph.Vertex):
            return ComparableVertex(other, self.attrs) in self._wrapped
        return NotImplemented
