"""
utilies that are used to descibe
"""

from typing import Iterable, Any, Tuple
import pandas as pd
import numpy as np
import utils
import mod


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
    how much each rule is used in respect to the resulting mass spec peakss
    """
    all_active_rules = set()

    pubchem_spectra = utils.get_spectra_from_pubchem(utils.graph_from_term(molecule).smiles)
    mod_spectrum_dict = utils.get_spectra_from_mod_derivation_graph(derivation_graph)
    mod_spectrum_df = pd.DataFrame(mod_spectrum_dict, columns=["mass", "intensity", "rules"])

    pubchem_masses = None
    if pubchem_spectra:
        # flatten all PubChem masses
        pubchem_masses = np.unique([
            int(p[0])
            for spec in pubchem_spectra
            for p in next(iter(spec.values()))
        ]).astype(float)

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

    """
    spectrum description
    """

    pubchem_spectra = utils.get_spectra_from_pubchem(utils.graph_from_term(molecule).smiles)
    mod_spectrum_dict = utils.get_spectra_from_mod_derivation_graph(derivation_graph)

    dice_max = -1.0
    tpr_max = -1.0
    for pubchem_spectrum in pubchem_spectra:
        pubchem_masses = set(int(x[0]) for x in list(pubchem_spectrum.values())[0])
        moel_masses = set(int(x[0]) for x in mod_spectrum_dict)

        dice_max = max(dice_max, dice_coefficient(pubchem_masses, moel_masses))
        tpr_max = max(tpr_max, len(pubchem_masses & moel_masses) / len(pubchem_masses))

    return (dice_max, tpr_max)
