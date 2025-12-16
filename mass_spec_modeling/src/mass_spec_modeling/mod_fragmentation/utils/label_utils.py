"""
Label helpers extracted from rule_extention.
"""
import re
from .term_transfers import decode_vertex_label

def mol_cleaned_label_str(strlab: str) -> str:
    pattern = re.compile(r'^a\(([^"(),\s]+),\s*(-?\d+),\s*(-?\d+)\)$')
    if pattern.match(strlab):
        strlab = decode_vertex_label(strlab)
    return strlab.replace("+", "").replace("-", "").replace(".", "")
