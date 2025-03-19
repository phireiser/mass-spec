import requests, json, warnings

def pubChemSmilesLookUp(smiles):
    pug_pre_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
    url = pug_pre_url + smiles + '/cids/JSON'
    response = requests.get(url)
    response.raise_for_status()
    cids = response.json()['IdentifierList']['CID']
    cid = cids[0]
    if len(cids) > 1:
        warnings.warn("Expecting only one PubChem CID", UserWarning)
    return cid

def getSpectraFromPubChem(cid):

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    mass_spec_data = []
    fields_of_interest = {
    "Top 5 Peaks",
    "m/z Top Peak",
    "m/z 2nd Highest",
    "m/z 3rd Highest"
    }
    # Extract Sections related to Mass Spectrometry
    sections = data.get("Record", {}).get("Section", [])
    for section in sections:
        if section.get("TOCHeading") == "Spectral Information":
            for sub_section in section.get("Section", []):
                if sub_section.get("TOCHeading") == "Mass Spectrometry":
                    for subsub in sub_section.get("Section", []):
                        if subsub.get("TOCHeading") == "GC-MS":
                            for item in subsub["Information"]:
                                name = item.get("Name", "")
                                found_top_five = False
                                if name in fields_of_interest:
                                    reference_number = item.get("ReferenceNumber")
                                    raw_value = item.get("Value", {})
                                    if "StringWithMarkup" in raw_value:
                                        top_peaks = []
                                        for line in raw_value["StringWithMarkup"]:
                                            text = line["String"]
                                            parts = text.split()
                                            if len(parts) == 2:
                                                try:
                                                    mz = float(parts[0])
                                                    intensity = float(parts[1])
                                                    top_peaks.append((mz, intensity))
                                                except ValueError:
                                                    pass
                                        extracted_value = top_peaks
                                    elif found_top_five:
                                        if name in ("m/z Top Peak", "m/z 2nd Highest", "m/z 3rd Highest"):
                                            number_list = val.get("Number", [])
                                            if len(number_list) == 1:
                                                mz_value = float(number_list[0])
                                                # use arbitrary intensity = 1.0
                                                extracted_value.append((mz_value, 1.0))
                                    else:
                                        extracted_value = None

                                    if not extracted_value == None:
                                        mass_spec_data.append({
                                            "ReferenceNumber": reference_number,
                                            "Value": extracted_value
                                        })
    if mass_spec_data:
        return mass_spec_data
    else:
        return "No mass spectrometry data found."