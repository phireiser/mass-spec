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


# A named placeholder atom label in a string-mode rule GML: an underscore-led token up to
# its charge/radical decoration or the closing quote, e.g. `label "_A"`, `label "_B+."`.
_RULE_PLACEHOLDER_RE = re.compile(r'label "(_\w+)')


def _placeholders_in_rule(rule: mod.Rule, default: str) -> List[str]:
    """Distinct placeholder names (without the leading ``_``) used by ``rule``.

    Falls back to ``[default]`` when the rule has no ``_``-placeholder, preserving the old
    always-constrain-``_A`` behaviour for rules that do not use one (harmless: mod ignores
    a ``constrainLabelAny`` naming a label the rule never mentions).
    """
    names = {m.group(1)[1:] for m in _RULE_PLACEHOLDER_RE.finditer(rule.getGMLString())}
    return sorted(names) if names else [default]


def apply_constraints(
    rules: List[mod.Rule],
    all_occuring_atoms: List[str],
    placeholder: str = "A"
    ) -> List[mod.Rule]:
    """
    Splice a ``constrainLabelAny`` block with the occurring atoms into each rule, once per
    distinct placeholder the rule uses.

    A rule may now carry more than one placeholder (``_A``, ``_B``, ...): since
    ``encode_vertex_label`` keeps distinct names as independent term variables, each must
    get its own ``constrainLabelAny`` block or an unconstrained ``_B`` would match any
    element (including hydrogen). Rules that use only ``_A`` -- i.e. every rule authored
    before this change -- are constrained exactly as before.
    """
    if not all_occuring_atoms:
        # `constrainLabelAny` with an empty `labels [ ]` block is not valid GML
        # (mod: "Expected 1 of String(label). Got only 0."), and semantically a
        # wildcard restricted to nothing could never match anyway. Refuse loudly
        # rather than emit a rule file mod will reject deep inside the loop.
        raise ValueError(
            "apply_constraints: no occurring atoms were detected, so the "
            f"'_{placeholder}' wildcard cannot be constrained. This means "
            "all_occuring() matched none of the element labels -- check that it "
            "is comparing undecorated atom symbols."
        )
    labels = sorted(all_occuring_atoms)
    constraint_rules = []
    for rule in rules:
        constraint_string = "".join(
            constrain_label_any(labels, ph) for ph in _placeholders_in_rule(rule, placeholder)
        )
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

def _undecorated_symbol(string_label: str) -> str:
    """
    Strip charge/radical decoration off a string-mode atom label: ``'O+'`` -> ``'O'``,
    ``'C+.'`` -> ``'C'``, ``'Cl-'`` -> ``'Cl'``. Mirrors the split done by
    :func:`data_generation.utils.term_transfers.encode_vertex_label` (kept local to
    avoid an import cycle).
    """
    i = 0
    while i < len(string_label) and string_label[i] not in "+-.":
        i += 1
    return string_label[:i]


def all_occuring(
    in_molecule_list: Iterable[mod.Graph],
    element_list: Iterable[str],
    ) -> Set[str]:
    """
    Collect all elements from element_list that occur in any graph from in_molecule_list.

    Matching is on the *undecorated* atom symbol, not the raw vertex label. The
    previous ``vLabelCount(e)`` form asked mod for an exact label match, so a
    charged or radical atom was invisible: in carbon monoxide, written
    ``[C-]#[O+]``, the labels are ``'C-'`` and ``'O+'``, neither of which equals
    ``'C'`` or ``'O'``. Every atom in that molecule is charged, so the result was
    the EMPTY set, which then produced an invalid ``constrainLabelAny`` block with
    no labels and killed the whole run (mod: "Expected 1 of String(label). Got only
    0."). Reading the vertices directly also drops the O(|element_list|) scan --
    ALL_ATOMS is ~100 entries -- in favour of one pass over the atoms.
    """

    wanted = set(element_list)
    occuring = set()
    for m in in_molecule_list:
        for v in m.vertices:
            symbol = _undecorated_symbol(v.stringLabel)
            if symbol in wanted:
                occuring.add(symbol)

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


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "apply_constraints",
    "get_constraint",
    "all_occuring",
    "add_constraints",
    "convert_to_moel_rule",
    "label_constraints_gml",
    "label_constraints_dfs",
    "split_rule_dfs",
    "flatten_list",
    "ALL_ATOMS",
    "ALK_NES_LABELS",
]
