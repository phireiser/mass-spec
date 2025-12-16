"""
String templates and helpers for building constraint GML/DFS snippets.
"""
from typing import List


def constrain_label_any(labels: List[str], placeholder: str = "A") -> str:
    quoted = " ".join(f'label "{x}"' for x in labels)
    return f"""
    constrainLabelAny [
        label "_{placeholder}"
        labels [ {quoted} ]
    ]
    """
