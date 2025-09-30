"""
utilies that are used to descibe
"""

from typing import Iterable, Any, Tuple
import pandas as pd
import numpy as np

import mod
from .spect_pubchem import get_spectra_from_pubchem
from .spect_mol import get_spectra_from_mod_derivation_graph
from .term_transfers import graph_from_term


def dice_coefficient(a: Iterable[Any], b: Iterable[Any]) -> float:
    """Calculates the Dice coefficient between two iterables."""
    set_a, set_b = set(a), set(b)
    return 2 * len(set_a & set_b) / (len(set_a) + len(set_b))


def overlap_coefficient(a: Iterable[Any], b: Iterable[Any]) -> float:
    """Calculates the Overlap coefficient between two iterables."""
    set_a, set_b = set(a), set(b)
    res = 0.0
    try:
        res = len(set_a & set_b) / min(len(set_a), len(set_b))
    except ZeroDivisionError:
        res = 0.0
    return res

def rule_usage(
    derivation_graph: mod.DG,
    molecule: mod.Graph,
    rules: Iterable[mod.Rule]
    ) -> pd.DataFrame:

    """
    how much each rule is used in respect to the resulting mass spec peaks
    """
    all_active_rules = set()

    pubchem_spectra = get_spectra_from_pubchem(graph_from_term(molecule).smiles)
    mod_spectrum_dict = get_spectra_from_mod_derivation_graph(derivation_graph)
    mod_spectrum_df = pd.DataFrame(mod_spectrum_dict, columns=["mass", "intensity", "rules"])

    print(mod_spectrum_df)
    df_long = (mod_spectrum_df.assign(rule=mod_spectrum_df['rules'].map(list))
             .explode('rule')
             .drop(columns='rules')
             .rename(columns={'rule': 'rule_id'}))
    df_long["mass"] = df_long["mass"].astype(int)

    masses_per_rule = (df_long.groupby('rule_id')['mass']
                   .apply(lambda s: sorted(set(s)))
                   .reset_index(name='masses'))

    print(masses_per_rule)

    pubchem_masses = None
    if pubchem_spectra:
        # flatten all PubChem masses
        pubchem_masses = np.unique([int(peak[0]) for peak in pubchem_spectra] ).astype(float)

    if pubchem_masses.size:
        # distance of every mod mass to the closest PubChem mass
        diffs_min = np.abs(mod_spectrum_df["mass"].to_numpy()[:, None] - pubchem_masses).min(axis=1)
        matched_rules = mod_spectrum_df.loc[diffs_min <= 1.1, "rules"]
        all_active_rules = set().union(*matched_rules.tolist())

    # build a DataFrame of ALL Rules anywhere
    rules_df = (
        pd.DataFrame(
            [(r.id, r.name) for r in set(rules)],  # rows: (id, name)
            columns=["id", "name"],
        )
        .drop_duplicates("id")        # if the two lists could overlap
        .assign(active=False)
        .set_index("id")
    )

    rules_df.loc[rules_df.index.isin(all_active_rules), "active"] = True
    rules_df = rules_df[[col for col in rules_df.columns if col != "name"] + ["name"]]

    return rules_df

def spectrum_statistic(
    derivation_graph: mod.DG,
    molecule: mod.Graph
    ) -> Tuple[float, float]:
    """spectrum description"""
    molecule = graph_from_term(molecule)
    smiles = molecule.smiles
    pubchem_spectra = get_spectra_from_pubchem(smiles)
    mod_spectrum_dict = get_spectra_from_mod_derivation_graph(derivation_graph)

    dice_max, tpr_max = -1.0, -1.0
    moel_masses_union, pubchem_masses_union = set(), set()
    for pubchem_spectrum in pubchem_spectra:
        pubchem_masses = {pubchem_spectrum[0]}
        moel_masses = set(int(x[0]) for x in mod_spectrum_dict)

        # filter out dimers/clusters (fragments that are bigger than the analyzed molectule)
        pubchem_masses = {n for n in pubchem_masses if n <= molecule.exactMass}

        moel_masses_union.update(moel_masses)
        pubchem_masses_union.update(pubchem_masses)

        dice_max = max(dice_max, dice_coefficient(pubchem_masses, moel_masses))
        try:
            tpr_max = max(tpr_max, len(pubchem_masses & moel_masses) / len(pubchem_masses))
        except ZeroDivisionError:
            pass


    return {
            "Dice_max": dice_max,
            "TPR_max": tpr_max,
            "MØD masses": sorted(moel_masses_union),
            "PubChem masses": sorted(pubchem_masses_union),
            "MØD support": len(moel_masses_union),
            "PubChem support": len(pubchem_masses_union),
           }
