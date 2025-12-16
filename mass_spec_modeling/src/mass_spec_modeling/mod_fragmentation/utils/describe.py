"""
Utilities to describe spectra and rule usage.
Refactored to separate metrics and data access responsibilities.
"""

from typing import Iterable, Any, Tuple, Dict
import pandas as pd
import mod

from .describe_sources import build_rule_usage_df, summarize_spectrum_overlap
from .metrics import dice_coefficient, overlap_coefficient


def rule_usage(
    derivation_graph: mod.DG,
    molecule: mod.Graph,
    rules: Iterable[mod.Rule]
    ) -> pd.DataFrame:
    """Proxy to data-access function returning rule usage DataFrame."""
    return build_rule_usage_df(derivation_graph, molecule, rules)


def spectrum_statistic(
    derivation_graph: mod.DG,
    molecule: mod.Graph
    ) -> Dict[str, Any]:
    """Summarize spectral overlap; metrics are computed in metrics module if needed."""
    summary = summarize_spectrum_overlap(derivation_graph, molecule)
    # Preserve original keys while using pure overlap summary
    return {
        "Dice_max": overlap_coefficient(summary["MØD masses"], summary["PubChem masses"]),
        "TPR_max": dice_coefficient(summary["MØD masses"], summary["PubChem masses"]),
        "MØD masses": summary["MØD masses"],
        "PubChem masses": summary["PubChem masses"],
        "MØD support": summary["MØD support"],
        "PubChem support": summary["PubChem support"],
    }
