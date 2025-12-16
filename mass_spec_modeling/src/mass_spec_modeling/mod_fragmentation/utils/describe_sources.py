"""
Data access helpers for describing spectra and rule usage.
Fetch or transform spectra from PubChem and MOD, but do not compute metrics here.
"""
from typing import Iterable, Any, Tuple, Dict, Optional, List
import pandas as pd
import numpy as np
import mod
from .spect_pubchem import get_spectra_from_pubchem
from .spect_mol import get_spectra_from_mod_derivation_graph
from .term_transfers import graph_from_term


def build_rule_usage_df(derivation_graph: mod.DG,
                        molecule: mod.Graph,
                        rules: Iterable[mod.Rule]) -> pd.DataFrame:
    """Return DataFrame with rule id, name, active flag based on MOD vs PubChem masses overlap."""
    all_active_rules = set()

    pubchem_spectra = get_spectra_from_pubchem(graph_from_term(molecule).smiles)
    mod_spectrum_dict = get_spectra_from_mod_derivation_graph(derivation_graph)
    mod_spectrum_df = pd.DataFrame(mod_spectrum_dict, columns=["mass", "intensity", "rules"])

    df_long = (mod_spectrum_df.assign(rule=mod_spectrum_df['rules'].map(list))
               .explode('rule')
               .drop(columns='rules')
               .rename(columns={'rule': 'rule_id'}))
    df_long["mass"] = df_long["mass"].astype(int)

    if pubchem_spectra:
        pubchem_masses = np.unique([int(peak[0]) for peak in pubchem_spectra]).astype(float)
        diffs_min = np.abs(mod_spectrum_df["mass"].to_numpy()[:, None] - pubchem_masses).min(axis=1)
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


def summarize_spectrum_overlap(derivation_graph: mod.DG,
                                molecule: mod.Graph) -> Dict[str, Any]:
    """Return overlap summary without computing advanced metrics here."""
    molecule_smiles = graph_from_term(molecule).smiles
    pubchem_spectra = get_spectra_from_pubchem(molecule_smiles)
    mod_spectrum_dict = get_spectra_from_mod_derivation_graph(derivation_graph)

    moel_masses_union, pubchem_masses_union = set(), set()
    for pubchem_spectrum in pubchem_spectra:
        pubchem_masses = {pubchem_spectrum[0]}
        moel_masses = set(int(x[0]) for x in mod_spectrum_dict)
        pubchem_masses = {n for n in pubchem_masses if n <= graph_from_term(molecule).exactMass}
        moel_masses_union.update(moel_masses)
        pubchem_masses_union.update(pubchem_masses)

    return {
        "MØD masses": sorted(moel_masses_union),
        "PubChem masses": sorted(pubchem_masses_union),
        "MØD support": len(moel_masses_union),
        "PubChem support": len(pubchem_masses_union),
    }
