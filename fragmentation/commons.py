import requests, json, warnings


def addConstraints(rule, conStringGML):
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = ruleGMLString(gmlstr[:-1] + conStringGML + gmlstr[-1], name)
    return rule

def printGrammar():
        post.summarySection("Molecule(s)")
        p = GraphPrinter()
        p.setMolDefault()
        #p.withIndex = True
        for m in inputGraphs:
                m.print(p)

        post.summarySection("Rule(s)")
        p = GraphPrinter()
        p.setReactionDefault()
        p.withIndex = True
        for r in inputRules:
                r.print(p)

def flatten_list(nested_list):
    """
    Flattens a nested list into a single list.
    
    :param nested_list: A list which may contain other lists
    :return: A flattened list
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

def labelConstraints(rule, rpl_dict, morphisms=None):
    """
    every underscore single Letter combination should be replaced according to rpl dict

    :param rule: a moel ruel
    :param rpl_dict: dictionary with key as lable to be replaced and a string or list of strings to substitue with
    :return: list of rules
    """
    gmlString = rule.getGMLString()
    rules = list()
    for old, new in rpl_dict.items():
        if isinstance(new, list):
            for new_i in new:
                rules.append(Rule.fromGMLString(gmlString.replace(old, new_i)))
        elif isinstance(new, str):
            rules.append(Rule.fromGMLString(gmlString.replace(old, new)))
        else:
            raise ValueError("new in rpl_dict is not of appropiate structure")

    return rules

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

def getSpectraFromPubChem(smiles):

    cid = pubChemSmilesLookUp(smiles)

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    mass_spec_data = []
    fields_of_interest = [
    "Top 5 Peaks",
    "m/z Top Peak",
    "m/z 2nd Highest",
    "m/z 3rd Highest"
    ]

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
                                        if name in fields_of_interest[-3:]:
                                            number_list = val.get("Number", [])
                                            if len(number_list) == 1:
                                                mz_value = float(number_list[0])
                                                # use arbitrary intensity = 1.0
                                                extracted_value.append((mz_value, 1.0))
                                    else:
                                        extracted_value = None

                                    if not extracted_value == None:
                                        mass_spec_data.append({
                                            reference_number: extracted_value
                                        })
    if mass_spec_data:
        return mass_spec_data
    else:
        return "No mass spectrometry data found."


def getParetRulesForGraph(derivationGraph, search_target_graph):
    parentRules = list()


    edges = derivationGraph.findVertex(search_target_graph).inEdges
    for edge in edges:
        try:
            for rule in edge.rules:
                parentRules.append(rule.id)
        except:
            #print("no rule in edge")
            pass
    return parentRules



def getSpectraFRomMoelDerivationGraph(derivationGraph):
    spectra = []
    sourceGraph = derivationGraph.graphDatabase[0]

    for graph in dg.createdGraphs:
            if graph.isMolecule:
                    if '+' in graph.getGMLString(): # only charged fragments can be detected
                            found = False # update spectra list if allready occuring

                            rules = set(getParetRulesForGraph(derivationGraph,graph))
                            
                            for i, (mass, occurence, old_rules) in enumerate(spectra):
                                    if abs(mass - graph.exactMass) < 1e-2:
                                            spectra[i] = (graph.exactMass, occurence + 1, old_rules.union(rules))
                                            found = True
                                            break
                            if not found: # add to spectra list if not occuring
                                    spectra.append((graph.exactMass, 1, rules))
            else:
                print("there are some graphs that are not molecules")
    return spectra

def dice_coefficient(a, b): # like F1 Socre
    set_a, set_b = set(a), set(b)
    return 2 * len(set_a & set_b) / (len(set_a) + len(set_b))

def overlap_coefficient(a, b):
    set_a, set_b = set(a), set(b)
    return len(set_a & set_b) / min(len(set_a), len(set_b))