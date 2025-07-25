"""
pubchem specifitcs to get EI spectra
"""
from typing import List, Tuple, Dict, Any
import requests

def pubchem_smiles_lookup(smiles: str) -> int:
    """
    Get the through PubChem's PUG the compound ID (CID) by SMILES string

    Parameters
    ----------
    smiles : str
        The SMILES string for the compound.

    Returns
    -------
    int
        PubChem CID for the given SMILES.
    """
    pug_pre_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
    url = f"{pug_pre_url}{smiles}/cids/JSON"

    try:
        response = requests.get(url, timeout= 8.0)
        response.raise_for_status()
        cids = response.json().get('IdentifierList', {}).get('CID', [])
        if not cids:
            raise ValueError(f"No PubChem CID found for SMILES: {smiles}")
        if len(cids) > 1:
            raise RuntimeWarning(f"Multiple PubChem CIDs found for SMILES: {smiles} -> {cids}")
        return int(cids[0])
    except requests.Timeout as e:
        print(f"Request to PubChem timed out after {8.0} seconds")
        raise e
    except requests.RequestException as e:
        print(f"Failed to fetch CID for {smiles}: {e}")
        raise e



def get_spectra_from_information_section(
    information: List[Dict[str, Any]]
    ) -> List[Dict[int, List[Tuple[float, float]]]]:

    """
    getting the spectra from a pubchem section
    """

    fields_of_interest = [
        "Top 5 Peaks",
        "m/z Top Peak",
        "m/z 2nd Highest",
        "m/z 3rd Highest"
    ]

    mass_spec_data = []

    for item in information:
        extracted_value = []
        name = item.get("Name", "")
        reference_number = item.get("ReferenceNumber")
        value = item.get("Value", [])
        if name in fields_of_interest[0]: # top 5 peaks
            for line in value["StringWithMarkup"]:
                parts = line["String"].split()
                if len(parts) == 2:
                    try:
                        mz = float(parts[0])
                        intensity = float(parts[1])
                        extracted_value.append((mz, intensity))
                    except ValueError as e:
                        print("expect a float")
                        raise e

            mass_spec_data.append({reference_number: extracted_value})
            extracted_value = []
        elif name in fields_of_interest[1:]: # top 3
            number_list = value.get("Number", [])
            if len(number_list) == 1:
                mz_value = float(number_list[0])
                # use arbitrary intensity = 1.0
                extracted_value.append((mz_value, 1.0))
                if name in fields_of_interest[3]:
                    mass_spec_data.append({reference_number: extracted_value})
                    extracted_value = []
    return mass_spec_data


def get_information_section_from_pubchem(cid: int) -> List[Dict[str, Any]] | None:
    """
    get the information section from pubchem
    """

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"

    response = requests.get(url, timeout= 8.0)
    response.raise_for_status()
    data = response.json()

    # Extract Sections related to Mass Spectrometry
    sections = data.get("Record", {}).get("Section", [])
    for section in sections:
        if section.get("TOCHeading") == "Spectral Information":
            for sub_section in section.get("Section", []):
                if sub_section.get("TOCHeading") == "Mass Spectrometry":
                    for subsub in sub_section.get("Section", []):
                        if subsub.get("TOCHeading") == "GC-MS":
                            return subsub["Information"]
                        else:
                            raise RuntimeError("no GC-MS in pubchem found for compound", cid)
    return None


def get_spectra_from_pubchem(
    smiles: str
    ) -> List[Dict[int, List[Tuple[float, float]]]]:

    """
    chaining of the pubchem functions to get spectra
    """


    cid = pubchem_smiles_lookup(smiles)
    info = get_information_section_from_pubchem(cid)
    spectra = get_spectra_from_information_section(info)
    return spectra
