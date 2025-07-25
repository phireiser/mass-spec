"""
everything related to constraints in the term mode
"""

from typing import List, Tuple, Iterable, Set, Dict, Any, Union
import itertools
import re
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
    constraint_string = get_constraint(all_occuring_atoms, placeholder)

    constraint_rules = list()
    for rule in rules:
        constraint_rules.append(
            add_constraints(rule, constraint_string)
        )
    return constraint_rules

def get_constraint(atoms: List[str], repl_label: str) -> str:
    """
    creates a string to be splised into the GML definition
    """

    labels = " ".join('label ' + '"' + x + '"' for x in atoms)

    return f"""
    constrainLabelAny [
        label "_{repl_label}"
        labels [ {labels} ]
    ]
    """

def all_occuring(
    in_molecule_list: mod.Graph,
    element_list: Iterable[str]
    ) -> Set[str]:

    """
    all lables that are in element list are collected if they are in the molecule graph
    """

    occuring = set()
    for m in in_molecule_list:
        for e in element_list:
            if m.vLabelCount(e) > 0:
                occuring.add(e)

    return occuring


def add_constraints(rule: mod.Rule, con_string_gml: str) -> mod.Rule:
    """
    splices the constraint string into the rule
    """
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = mod.ruleGMLString(gmlstr[:-1] + con_string_gml + gmlstr[-1], name)
    return rule


def convert_to_moel_rule(tupel: Iterable) -> List[mod.Rule]:
    """
    converts a ruel defined as a tupel of name and DFS string to a mod ruel
    """
    if isinstance(tupel, tuple):
        tupel = [tupel]
    return [mod.Rule.fromDFS(rule, name= name) for rule, name in tupel ]


def label_constraints_gml(
    input_rules: mod.Rule | List[mod.Rule],
    rpl_dict: Dict[str, str | List[str]]
    ) -> List[List[mod.Rule]]:

    """
    every underscore single Letter combination should be replaced according to rpl dict
    """

    if not isinstance(input_rules, list):
        input_rules = [input_rules]
    return_rules = []
    for rule in input_rules:
        gml_string = rule.getGMLString()
        rules = []
        for old_structure, new_structure in rpl_dict.items():
            if not isinstance(new_structure, list):
                new_structure = list(new_structure)
            for new_i in new_structure:
                altered_string_obj = gml_string.replace(old_structure, new_i)
                altered_rule_obj = mod.Rule.fromGMLString(altered_string_obj)
                altered_rule_obj.name = rule.name + " " + new_i
                rules.append(altered_rule_obj)
        return_rules.append(rules)

    return return_rules


def label_constraints_dfs(
    input_rules: mod.Rule | List[mod.Rule],
    to_replace: List[str],
    replacements: List
    ) -> List[Tuple[str, str]]:

    """
    every element from to_replace should be replaced according to replacements
    but with all possible combinations
    """

    # https://www.mathsisfun.com/combinatorics/combinations-permutations.html
    # https://docs.python.org/3/library/itertools.html
    return_rules = []

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
                            'a1': max_node_id + 1, 'a2': max_node_id + 2,
                            'a3': max_node_id + 3, 'a4': max_node_id + 4,
                            'a5': max_node_id + 5, 'a6': max_node_id + 6,}
                repl = repl.format(**values)

                for radical_ion in [ "", "+", ".", "+.", ".+"]:
                    for i in range(1, max_node_id+1):
                        new_rule = new_rule.replace(
                            '[' + target + radical_ion + ']' +
                            str(i), repl[:2] + radical_ion + repl[2:], -1
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
