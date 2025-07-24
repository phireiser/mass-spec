from typing import List, Tuple, Iterable, Set
from typing import Hashable, Dict, Optional, Any, Union

def pubChemSmilesLookUp(smiles: str) -> int:
    pug_pre_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
    url = pug_pre_url + smiles + '/cids/JSON'
    response = requests.get(url)
    response.raise_for_status()
    cids = response.json()['IdentifierList']['CID']
    cid = int(cids[0])
    if len(cids) > 1:
        raise RuntimeWarning("Expecting only one PubChem CID")
    return cid


def getSpectraFromInformationSection(
    information: List[Dict[str, Any]]
    ) -> List[Dict[int, List[Tuple[float, float]]]]:

    fields_of_interest = [
        "Top 5 Peaks",
        "m/z Top Peak",
        "m/z 2nd Highest",
        "m/z 3rd Highest"
    ]

    mass_spec_data = list()
    extracted_value = list()

    for item in information:
        name = item.get("Name", "")
        reference_number = item.get("ReferenceNumber")
        value = item.get("Value", [])
        if name in fields_of_interest:
            if name in fields_of_interest[0]: # top 5 peaks
                for line in value["StringWithMarkup"]:
                    text = line["String"]
                    parts = text.split()
                    if len(parts) == 2:
                        try:
                            mz = float(parts[0])
                            intensity = float(parts[1])
                            extracted_value.append((mz, intensity))
                        except ValueError:
                            raise RuntimeWarning("not a float")
                            pass
                mass_spec_data.append({reference_number: extracted_value})
                extracted_value = list()
            elif name in fields_of_interest[1:]: # top 3
                number_list = value.get("Number", [])
                if len(number_list) == 1:
                    mz_value = float(number_list[0])
                    # use arbitrary intensity = 1.0
                    extracted_value.append((mz_value, 1.0))
                    if name in fields_of_interest[3]:
                        mass_spec_data.append({reference_number: extracted_value})
                        extracted_value = list()
    return mass_spec_data


def getInformationSectionFromPubChem(cid: int) -> List[Dict[str, Any]] | None:

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"

    response = requests.get(url)
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
    cid = pubChemSmilesLookUp(smiles)
    info = getInformationSectionFromPubChem(cid)
    spectra = getSpectraFromInformationSection(info)
    return spectra
