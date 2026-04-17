"""
Utilities to describe spectra and rule usage.
Refactored to separate metrics and data access responsibilities.
"""

from typing import Iterable, Any, Dict, Iterable, Any, Dict, List
import pandas as pd
import numpy as np
import mod

from .metrics import dice_coefficient, overlap_coefficient
from .spect_pubchem import get_spectra_from_pubchem
from .spect_jdx import get_spectra_from_local_jdx
from .spect_mol import get_spectra_from_mod_derivation_graph
from .term_transfers import graph_from_term

from src.project_paths import shared_path


#get_spectra = lambda smiles, name: get_spectra_from_pubchem(smiles)
get_spectra = lambda smiles, name: get_spectra_from_local_jdx(name, shared_path("NIST_SPECTRA_DIR_REL"))

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
        "Dice_max": overlap_coefficient(summary["MØD masses"], summary["ground_truth masses"]),
        "TPR_max": dice_coefficient(summary["MØD masses"], summary["ground_truth masses"]),
        "MØD masses": summary["MØD masses"],
        "ground_truth masses": summary["ground_truth masses"],
        "MØD support": summary["MØD support"],
        "ground_truth support": summary["ground_truth support"],
    }


def build_rule_usage_df(
    derivation_graph: mod.DG,
    molecule: mod.Graph,
    rules: Iterable[mod.Rule]
    ) -> pd.DataFrame:
    """Return DataFrame with rule id, name, active flag based on MOD vs ground_truth masses overlap."""
    all_active_rules = set()

    ground_truth_spectra = get_spectra(graph_from_term(molecule).smiles, graph_from_term(molecule).name)
    mod_spectrum_dict = get_spectra_from_mod_derivation_graph(derivation_graph)
    mod_spectrum_df = pd.DataFrame(mod_spectrum_dict, columns=["mass", "intensity", "rules"])

    df_long = (mod_spectrum_df.assign(rule=mod_spectrum_df['rules'].map(list))
               .explode('rule')
               .drop(columns='rules')
               .rename(columns={'rule': 'rule_id'}))
    df_long["mass"] = df_long["mass"].astype(int)

    if ground_truth_spectra:
        ground_truth_masses = np.unique([int(peak[0]) for peak in ground_truth_spectra]).astype(float)
        diffs_min = np.abs(mod_spectrum_df["mass"].to_numpy()[:, None] - ground_truth_masses).min(axis=1)
        matched_rules = mod_spectrum_df.loc[diffs_min <= 1.1, "rules"]
        all_active_rules = set().union(*matched_rules.tolist())

    rules_df = (
        pd.DataFrame(
            [(r.id, r.name) for r in set(rules)],
            columns=["id", "name"],
        )
        .drop_duplicates("id")
        .assign(active=False)
        .set_index("id")
    )

    if all_active_rules:
        rules_df.loc[rules_df.index.isin(all_active_rules), "active"] = True
    rules_df = rules_df[[col for col in rules_df.columns if col != "name"] + ["name"]]

    return rules_df


def summarize_spectrum_overlap(
        derivation_graph: mod.DG,
        molecule: mod.Graph
        ) -> Dict[str, Any]:
    """Return overlap summary without computing advanced metrics here."""
    ground_truth_spectra = get_spectra(graph_from_term(molecule).smiles, graph_from_term(molecule).name)
    mod_spectrum_dict = get_spectra_from_mod_derivation_graph(derivation_graph)

    moel_masses_union, ground_truth_masses_union = set(), set()
    for ground_truth_spectrum in ground_truth_spectra:
        ground_truth_masses = {ground_truth_spectrum[0]}
        moel_masses = set(int(x[0]) for x in mod_spectrum_dict)
        ground_truth_masses = {n for n in ground_truth_masses if n <= graph_from_term(molecule).exactMass}
        moel_masses_union.update(moel_masses)
        ground_truth_masses_union.update(ground_truth_masses)

    return {
        "MØD masses": sorted(moel_masses_union),
        "ground_truth masses": sorted(ground_truth_masses_union),
        "MØD support": len(moel_masses_union),
        "ground_truth support": len(ground_truth_masses_union),
    }
