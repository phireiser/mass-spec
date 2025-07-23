"""
utilies that are used to descibe
"""

from typing import Iterable, Any, Tuple
import pandas as pd
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

    pubchem_spectra = getSpectraFromPubChem(graphFromTerm(molecule).smiles)
    mod_spectrum_dict = getSpectraFromMoelDerivationGraph(derivation_graph)
    mod_spectrum_df = pd.DataFrame(mod_spectrum_dict, columns=["mass", "intensity", "rules"])

    for pubchem_spectrum in pubchem_spectra:

        pubchem_masses = set([int(x[0]) for x in list(pubchem_spectrum.values())[0]])
        moel_masses = set([int(x[0]) for x in mod_spectrum_dict])

        # collect rules that created matching masses threshold +/- 1
        if len(mod_spectrum_df) > 0:
            rules_active_here = mod_spectrum_df[
                mod_spectrum_df["mass"].apply(
                    lambda m: any(abs(m - cm) <= 1.0 for cm in pubchem_masses)
                )
            ]["rules"]

            for rule_group in rules_active_here:
                all_active_rules.update(rule_group)

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

    pubchem_spectra = getSpectraFromPubChem(graphFromTerm(molecule).smiles)
    mod_spectrum_dict = getSpectraFromMoelDerivationGraph(derivation_graph)

    dice_max = -1.0
    tpr_max = -1.0
    for pubchem_spectrum in pubchem_spectra:
        pubchem_masses = set([int(x[0]) for x in list(pubchem_spectrum.values())[0]])
        moel_masses = set([int(x[0]) for x in mod_spectrum_dict])

        dice_max = max(dice_max, dice_coefficient(pubchem_masses, moel_masses))
        tpr_max = max(tpr_max, len(pubchem_masses & moel_masses) / len(pubchem_masses))

    return (dice_max, tpr_max)
