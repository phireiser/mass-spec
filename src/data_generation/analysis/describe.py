"""
Utilities to describe spectra and rule usage.
Refactored to separate metrics and data access responsibilities.
"""

from typing import Iterable, Any, Dict, Iterable, Any, Dict, List
import pandas as pd
import numpy as np
import mod

from .metrics import dice_coefficient, overlap_coefficient
from src.data_generation.utils.spect_pubchem import get_spectra_from_pubchem
from src.data_generation.utils.spect_jdx import get_spectra_by_smiles
from src.data_generation.utils.spect_mol import get_spectra_from_mod_derivation_graph
from src.data_generation.utils.term_transfers import graph_from_term

from src.project_paths import shared_path


#get_spectra = lambda smiles, name: get_spectra_from_pubchem(smiles)
get_spectra = lambda smiles, name: get_spectra_by_smiles(smiles, shared_path("PARQUET_DIR_REL"))


def _ground_truth_smiles(molecule: mod.Graph, smiles: "str | None") -> str:
    """SMILES to look the reference spectrum up with.

    **Always pass the molecule's original ``smiles``.** Reconstructing it from the term
    graph (``graph_from_term(molecule).smiles``) silently loses the lookup for every
    molecule whose store identity depends on stereochemistry: the term encoding
    ``a(symbol, charge, radical)`` carries no stereo descriptors, so the round-tripped
    SMILES canonicalises to a different InChIKey and
    :func:`spect_jdx.get_spectra_by_smiles` (SMILES -> InChIKey -> CAS -> peaks) resolves
    no CAS and returns ``[]``.

    That failure is silent and total -- it zeroes the ground truth for BOTH arms of a
    comparison, so a real difference shows up as "0.00 coverage, unmeasurable" rather than
    as an error. Measured: sucrose 46 peaks by original SMILES vs **0** by round-trip,
    glucose 94 vs **0**; riboflavin (no stereocentres) 49 vs 49, which is why only the
    saccharides ever looked empty. With the lookup fixed, sucrose's migration coverage is
    TPR 0.068 -> 0.270, previously invisible.

    When ``smiles`` is None the round-trip is used for backward compatibility and the
    caller is warned, so the silent-zero case becomes visible instead of being read as a
    chemistry result.
    """
    if smiles:
        return smiles
    fallback = graph_from_term(molecule).smiles
    print(
        f"  [describe] WARNING: no original SMILES passed; looking the reference spectrum "
        f"up with the term round-trip '{fallback}'. Stereochemistry is NOT preserved by "
        f"the term encoding, so this returns NO peaks for stereo-dependent molecules "
        f"(e.g. sugars) and the resulting coverage will read as 0.00. Pass smiles=... ."
    )
    return fallback


def rule_usage(
    derivation_graph: mod.DG,
    molecule: mod.Graph,
    rules: Iterable[mod.Rule],
    smiles: "str | None" = None,
    ) -> pd.DataFrame:
    """Proxy to data-access function returning rule usage DataFrame."""
    return build_rule_usage_df(derivation_graph, molecule, rules, smiles)


def spectrum_statistic(
    derivation_graph: mod.DG,
    molecule: mod.Graph,
    smiles: "str | None" = None,
    ) -> Dict[str, Any]:
    """Summarize spectral overlap; metrics are computed in metrics module if needed.

    Pass ``smiles`` (the molecule's original SMILES) so the reference spectrum is found for
    stereo-dependent molecules -- see :func:`_ground_truth_smiles`.
    """
    summary = summarize_spectrum_overlap(derivation_graph, molecule, smiles)
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
    rules: Iterable[mod.Rule],
    smiles: "str | None" = None,
    ) -> pd.DataFrame:
    """Return DataFrame with rule id, name, active flag based on MOD vs ground_truth masses overlap.

    ``smiles`` is the molecule's original SMILES; pass it so stereo-dependent molecules
    resolve in the store (see :func:`_ground_truth_smiles`).
    """
    all_active_rules = set()

    ground_truth_spectra = get_spectra(
        _ground_truth_smiles(molecule, smiles), graph_from_term(molecule).name
    )
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
        molecule: mod.Graph,
        smiles: "str | None" = None,
        ) -> Dict[str, Any]:
    """Return overlap summary without computing advanced metrics here.

    ``smiles`` is the molecule's original SMILES; pass it so stereo-dependent molecules
    resolve in the store (see :func:`_ground_truth_smiles`).
    """
    ground_truth_spectra = get_spectra(
        _ground_truth_smiles(molecule, smiles), graph_from_term(molecule).name
    )
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


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "spectrum_statistic",
    "rule_usage",
    "overlap_coefficient",
    "dice_coefficient",
]
