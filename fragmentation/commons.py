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


def labelConstraints(input_rules, rpl_dict, morphisms=None):
    """
    every underscore single Letter combination should be replaced according to rpl dict

    :param rule: a moel ruel or list of them
    :param rpl_dict: dictionary with key as lable to be replaced and a string or list of strings to substitue with
    :return: list of rules
    """
    return_rules = list()
    for rule in input_rules:
        gmlString = rule.getGMLString()
        rules = list()
        for old_structure, new_structure in rpl_dict.items():
            if isinstance(new_structure, list):
                for new_i in new_structure:
                    alteredStringObj = gmlString.replace(old_structure, new_i)
                    alteredRuleObj = Rule.fromGMLString(alteredStringObj)
                    alteredRuleObj.name = rule.name + " " + new_i
                    rules.append(alteredRuleObj)
            elif isinstance(new_structure, str):
                alteredStringObj = gmlString.replace(old_structure, new_structure)
                alteredRuleObj = Rule.fromGMLString(alteredStringObj)
                alteredRuleObj.name = rule.name + " " + new_structure
                rules.append(alteredRuleObj)
            else:
                raise ValueError("new structure in rpl_dict is not of appropiate structure")
        return_rules.append(rules)
    return return_rules


def pubChemSmilesLookUp(smiles):
    pug_pre_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
    url = pug_pre_url + smiles + '/cids/JSON'
    response = requests.get(url)
    response.raise_for_status()
    cids = response.json()['IdentifierList']['CID']
    cid = cids[0]
    if len(cids) > 1:
        raise RuntimeWarning("Expecting only one PubChem CID")
    return cid


def getSpectraFromInformationSection(information):

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


def getInformationSectionFromPubChem(cid):

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

def getSpectraFromPubChem(smiles):
    cid = pubChemSmilesLookUp(smiles)
    info = getInformationSectionFromPubChem(cid)
    spectra = getSpectraFromInformationSection(info)
    return spectra


def getParetRulesForGraph(derivationGraph, search_target_graph):
    parentRules = list()
    parentGraph = list()
    edges = derivationGraph.findVertex(search_target_graph).inEdges
    
    for edge in edges:
        try:
            for rule in edge.rules:
                parentRules.append(rule.id)
        except:
            pass

    for e in edges:
        try:
            for s in e.sources:
               parentRules.extend(getParetRulesForGraph(derivationGraph, s.graph))
        except(mod.LogicError):
            pass

    return parentRules



def getSpectraFRomMoelDerivationGraph(derivationGraph):
    spectra = list()
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
                raise RuntimeWarning("there are some graphs that are not molecules")
    return spectra


def dice_coefficient(a, b): # like F1 Socre
    set_a, set_b = set(a), set(b)
    return 2 * len(set_a & set_b) / (len(set_a) + len(set_b))


def overlap_coefficient(a, b):
    set_a, set_b = set(a), set(b)
    res = 0
    try:
        res = len(set_a & set_b) / min(len(set_a), len(set_b))
    except(ZeroDivisionError):
        pass
    return res