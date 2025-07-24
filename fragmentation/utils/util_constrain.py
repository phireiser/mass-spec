"""
everything related to constraints in the term mode
"""

from typing import List, Tuple, Iterable, Set, Dict, Any, Union
import mod


hetroAtoms = [
    "He",
    "Li","Be","B","N","O","F","Ne",
    "Na","Mg","Al","Si","P","S","Cl","Ar",
    "K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr",
    "Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe",
    "Cs","Ba", "La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
    "Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn",
    "Fr","Ra", "Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es"
]

# TODO alkanes (single bond), alkenes(>=1 double bond), alkynes (>=1 tripple bond)
alk_nes_lables = ["H", "C"]

allAtoms = hetroAtoms
allAtoms.extend(alk_nes_lables)


# all Elements until Z = 99 as phase Z > 99 is unkown & origin = syntheic
# TODO ? functional group containing heteroAtom, this is only heteroAtoms itself


 # only create rules for occuring hetroAtoms
occuring_hetroAtoms = set(hetroAtoms)
occuring_allAtoms = set(allAtoms)


def apply_constraints(
    rules: List[mod.Rule],
    all_occuring_atoms: List[str],
    placeholder: str = "A"
    ) -> List[mod.Rule]:

    """
    takes the a list of atom lables and puts it in as a constraint for the rule
    """

    # contraints Label Any
    constraint_string = getConstraint(all_occuring_atoms, placeholder)

    constraint_rules = list()
    for rule in rules:
        constraint_rules.append(
            addConstraints(rule, constraint_string)
        )
    return constraint_rules

def getConstraint(atoms: List[str], repl_label: str) -> str:

    labels = " ".join('label ' + '"' + x + '"' for x in atoms)

    return f"""
    constrainLabelAny [
        label "_{repl_label}"
        labels [ {labels} ]
    ]
    """

def allOccuring(inMoleculeList: mod.Graph, elementList: Iterable[str]) -> Set[str]:
    occuring = set()
    for m in inMoleculeList:
        for e in elementList:
            if m.vLabelCount(e) > 0:
                occuring.add(e)
    return occuring


def addConstraints(rule: mod.Rule, conStringGML: str) -> mod.Rule:
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = mod.ruleGMLString(gmlstr[:-1] + conStringGML + gmlstr[-1], name)
    return rule


def convert2MoelRule(tupel: Iterable) -> List[mod.Rule]:
    if isinstance(tupel, tuple):
        tupel = [tupel]
    return [ Rule.fromDFS(rule, name= name) for rule, name in tupel ]


def labelConstraints_gml(
    input_rules: mod.Rule | List[mod.Rule],
    rpl_dict: Dict[str, str | List[str]]
    ) -> List[List[mod.Rule]]:
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


def labelConstraints_dfs(
    input_rules: mod.Rule | List[mod.Rule],
    to_replace: List[str],
    replacements #TODO
    ) -> List[Tuple[str, str]]:

    """
    every underscore single Letter combination should be replaced according to rpl dict

    :param rule: a moel ruel as a DFS string or list of them
    :param rpl_dict: dictionary with key as lable to be replaced and a string or list of strings to substitue with
    :return: list of rules
    """

    # https://www.mathsisfun.com/combinatorics/combinations-permutations.html
    # https://docs.python.org/3/library/itertools.html
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
                            '[' + target + radIon + ']' + str(i), repl[:2] + radIon + repl[2:], -1
                            )

            return_rules.append((new_rule, name))
    return return_rules

def split_rule_dfs(rule: str) -> Tuple[List[str], List[str]]:
    """
    Split a ruleDFS of the form
        graphs_left >> graphs_right
    into two lists while ignoring dots that are inside any brackets.

    Returns
    -------
    left_graphs  : list[str]
    right_graphs : list[str]
    """
    # separate left & right
    if ">>" not in rule:
        raise ValueError("ruleDFS must contain '>>'")
    left_raw, right_raw = map(str.strip, rule.split(">>", 1))

    # helper: top-level dot splitter using ONE depth counter
    def split_side(side: str) -> List[str]:
        graphs, buf, depth = [], [], 0
        for ch in side:
            if ch in "[({":        # any opening bracket
                depth += 1
            elif ch in "])}":      # any closing bracket
                depth -= 1

            if ch == "." and depth == 0:   # separator only at top level
                graph = "".join(buf).strip()
                if graph:
                    graphs.append(graph)
                buf.clear()
            else:
                buf.append(ch)

        last = "".join(buf).strip()
        if last:
            graphs.append(last)
        return graphs

    return split_side(left_raw), split_side(right_raw)


def flatten_list(nested_list: List[Union[Any, List]]) -> List[Any]:
    """
    Flattens a nested list into a single list.

    :param nested_list: A list which may contain other lists
    :return: A flattened list
    """
    flat_list: List[Any] = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list



