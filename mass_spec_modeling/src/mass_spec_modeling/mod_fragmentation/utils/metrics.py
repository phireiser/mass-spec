"""
Pure metrics utilities for spectra and sets.
"""
from typing import Iterable, Any, Dict, List
import numpy as np


def dice_coefficient(a: Iterable[Any], b: Iterable[Any]) -> float:
    set_a, set_b = set(a), set(b)
    denom = (len(set_a) + len(set_b))
    if denom == 0:
        return 0.0
    return 2 * len(set_a & set_b) / denom


def overlap_coefficient(a: Iterable[Any], b: Iterable[Any]) -> float:
    set_a, set_b = set(a), set(b)
    try:
        return len(set_a & set_b) / min(len(set_a), len(set_b))
    except ZeroDivisionError:
        return 0.0


def coverage_stats(mod_masses: Iterable[int], ref_masses: Iterable[int]) -> Dict[str, Any]:
    """Compute Dice_max and TPR_max across masses collections.
    Returns dict with dice, tpr, supports and sorted masses.
    """
    moel_masses = set(int(x) for x in mod_masses)
    ref_masses = set(int(x) for x in ref_masses)

    dice = dice_coefficient(moel_masses, ref_masses)
    try:
        tpr = len(moel_masses & ref_masses) / len(ref_masses)
    except ZeroDivisionError:
        tpr = 0.0

    return {
        "Dice": dice,
        "TPR": tpr,
        "MØD masses": sorted(moel_masses),
        "Ref masses": sorted(ref_masses),
        "MØD support": len(moel_masses),
        "Ref support": len(ref_masses),
    }
