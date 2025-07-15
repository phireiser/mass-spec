heteroAtoms = [
    "He","Li","Be","B","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca",
    "Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb",
    "Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe",
    "Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
    "Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra",
    "Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es"
]

alk_nes_lables = ["H", "C"] # alkanes (single bond), alkenes(>=1 double bond), alkynes (>=1 tripple bond)


# all Elements until Z = 99 as phase Z > 99 is unkown & origin = syntheic
# TODO ? functional group containing heteroAtom, this is only heteroAtoms itself


lables = " ".join('label ' + '"' + x + '"' for x in heteroAtoms)

constraint = """
constrainLabelAny [
    label "_Y"
    labels [ """ + lables + """ ]
]
"""

def addConstraints(rule, conStringGML):
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = ruleGMLString(gmlstr[:-1] + conStringGML + gmlstr[-1], name)
    return rule


def convert2MoelRule(tupel):
    if isinstance(tupel, tuple):
        tupel = [tupel]
    return [ Rule.fromDFS(rule, name= name) for rule, name in tupel ]


def labelConstraints_gml(input_rules, rpl_dict):
    """
    every underscore single Letter combination should be replaced according to rpl dict

    :param rule: a moel ruel or list of them
    :param rpl_dict: dictionary with key as lable to be replaced and a string or list of strings to substitue with
    :return: list of rules
    """
    if not isinstance(input_rules, list):
        input_rules = [input_rules]
    return_rules = list()
    for rule in input_rules:
        gmlString = rule.getGMLString()
        rules = list()
        for old_structure, new_structure in rpl_dict.items():
            if not isinstance(new_structure, list):
                new_structure = list(new_structure)
            for new_i in new_structure:
                alteredStringObj = gmlString.replace(old_structure, new_i)
                alteredRuleObj = Rule.fromGMLString(alteredStringObj)
                alteredRuleObj.name = rule.name + " " + new_i
                rules.append(alteredRuleObj)
        return_rules.append(rules) 
    return return_rules


def labelConstraints_dfs(input_rules, to_replace, replacements):
    """
    every underscore single Letter combination should be replaced according to rpl dict

    :param rule: a moel ruel as a DFS string or list of them
    :param rpl_dict: dictionary with key as lable to be replaced and a string or list of strings to substitue with
    :return: list of rules
    """

    #https://www.mathsisfun.com/combinatorics/combinations-permutations.html
    #https://docs.python.org/3/library/itertools.html
    return_rules = list()

    if not isinstance(input_rules, list):
        input_rules = [input_rules]
    for rule, name in input_rules:
        for combo in itertools.product(replacements, repeat=len(to_replace)):
            new_rule = rule
            for target, repl in zip(to_replace, combo):
                
                # determine atom node id start from max occuring id and build it
                nums = [int(n) for n in re.findall(r'\d+', new_rule)]
                max_node_id = max(nums)
                values = {
                            'a1': max_node_id + 1, 'a2': max_node_id + 2, 'a3': max_node_id + 3, 'a4': max_node_id + 4, 
                            'a5': max_node_id + 5, 'a6': max_node_id + 6,}
                repl = repl.format(**values)

                for radIon in [ "", "+", ".", "+.", ".+"]:
                    for i in range(1, max_node_id+1):
                        new_rule = new_rule.replace(
                            '[' + target + radIon + ']' + str(i), 
                            repl[:2] + radIon + repl[2:],
                            -1)
                            
            return_rules.append((new_rule, name))
    return return_rules
