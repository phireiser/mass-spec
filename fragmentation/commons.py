def addConstraints(rule, conStringGML):
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = ruleGMLString(gmlstr[:-1] + conStringGML + gmlstr[-1], name)
    return rule

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