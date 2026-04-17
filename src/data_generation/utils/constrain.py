"""
Everything related to constraints in the term mode.
"""

from typing import List, Tuple, Iterable, Set, Dict, Any, Union
import itertools
import re
import mod

from .element_sets import HETERO_ATOMS, ALK_NES_LABELS, ALL_ATOMS
from .constraint_templates import constrain_label_any

# only create rules for occurring atoms
occuring_hetero_atoms = set(HETERO_ATOMS)
occuring_all_atoms = set(ALL_ATOMS)


def apply_constraints(
    rules: List[mod.Rule],
    all_occuring_atoms: List[str],
    placeholder: str = "A"
    ) -> List[mod.Rule]:
    """
    Splice a constrainLabelAny block with selected labels into each rule.
    """
    constraint_string = constrain_label_any(all_occuring_atoms, placeholder)
    constraint_rules = []
    for rule in rules:
        constraint_rules.append(add_constraints(rule, constraint_string))
    return constraint_rules


def get_constraint(
    atoms: List[str],
    repl_label: str
    ) -> str:
    """
    Deprecated: use constrain_label_any() from constraint_templates.
    """
    return constrain_label_any(atoms, repl_label)

def all_occuring(
    in_molecule_list: Iterable[mod.Graph],
    element_list: Iterable[str],
    ) -> Set[str]:
    """
    Collect all labels from element_list that occur in any graph from in_molecule_list.
    """

    occuring = set()
    for m in in_molecule_list:
        for e in element_list:
            if m.vLabelCount(e) > 0:
                occuring.add(e)

    return occuring


def add_constraints(
    rule: mod.Rule,
    con_string_gml: str
    ) -> mod.Rule:
    """
    Splice the constraint string into the rule's GML.
    """
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = mod.Rule.fromGMLString(gmlstr[:-1] + con_string_gml + gmlstr[-1], name)
    return rule


def convert_to_moel_rule(tupel: Iterable) -> List[mod.Rule]:
    """
    Convert a rule defined as a (dfs, name) tuple into mod.Rule objects.
    """
    if isinstance(tupel, tuple):
        tupel = [tupel]
    return [mod.Rule.fromDFS(rule, name= name) for rule, name in tupel ]


def label_constraints_gml(
    input_rules: mod.Rule | List[mod.Rule],
    rpl_dict: Dict[str, str | List[str]]
    ) -> List[List[mod.Rule]]:

    """
    Replace every underscore-single-letter token according to rpl_dict.
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
    input_rules: List[Tuple[str, str]] | Tuple[str, str],
    to_replace: List[str],
    replacements: List[str]
    ) -> List[Tuple[str, str]]:

    """
    Replace each token in to_replace according to replacements, generating
    all possible combinations. Input rules are DFS strings paired with names.
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
