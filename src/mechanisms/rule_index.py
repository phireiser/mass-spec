"""
Build a cross-link index from the existing MØD ``Rule.fromDFS`` rules.

Each mechanism record we curate from the English 4th-ed. book links back to the MØD rule(s)
that encode the same reaction, joined on the **book equation ID** (e.g. ``4.13``). The MØD
rules cite the German Springer edition, whose equation numbering McLafferty preserves, so the
equation ID is a stable key across both editions.

This parses the rule modules with ``ast`` (no ``mod`` import, runs on the host) and extracts,
per ``mod.Rule.fromDFS(...)`` assignment: the variable name, the DFS string, the rule name,
the German page (``Seite N``) from the nearest preceding comment, and the equation ID (from
the ``IMS_<chap>_<eq>`` variable name, the name string, or a ``Gl. X.Y`` / ``#IMS_X_Y`` comment).

Output: ``data/mechanisms/rule_index.json`` with a flat ``entries`` list and a ``by_equation``
map used both for record cross-linking and as the coverage denominator.

    python src/mechanisms/rule_index.py
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

from src.project_paths import REPO_ROOT, shared_path

RULES_DIR = shared_path("RULES_DIR_REL")
DEFAULT_FILES = [
    RULES_DIR / "IMS_chap4_examples.py",
    RULES_DIR / "IMS_chap8_examples.py",
    RULES_DIR / "IMS_bookCover.py",
]
DEFAULT_OUT = shared_path("MECHANISMS_DIR_REL", "rule_index.json")

_SEITE = re.compile(r"Seite\s+(\d+)")
_GL = re.compile(r"Gl\.\s*(\d+\.\d+)")
_HASH_IMS = re.compile(r"#\s*IMS_(\d+)_(\d+)")
_VAR_IMS = re.compile(r"^IMS_(\d+)_(\d+)")
_NAME_EQ = re.compile(r"\b(\d+\.\d+)\b")


def _is_fromdfs(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "fromDFS"
    )


def _const_str(node: ast.AST | None) -> str | None:
    # Adjacent string literals are already concatenated into one Constant by the
    # parser, so a plain Constant str is all we expect here.
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _kwargs(call: ast.Call) -> dict[str, ast.AST]:
    return {kw.arg: kw.value for kw in call.keywords if kw.arg}


def _equation_from(var: str, name: str | None) -> str | None:
    m = _VAR_IMS.match(var)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    if name:
        m = _NAME_EQ.search(name)
        if m:
            return m.group(1)
    return None


def _scan_preceding_comments(lines: list[str], assign_lineno: int) -> dict:
    """Walk upward from an assignment for the nearest citation comment block."""
    page = equation = None
    i = assign_lineno - 2  # 0-based line just above the assignment
    scanned = 0
    while i >= 0 and scanned < 10:
        stripped = lines[i].strip()
        if stripped == "":
            i -= 1
            scanned += 1
            continue
        if not stripped.startswith("#"):
            break  # hit code above; stop
        if page is None:
            m = _SEITE.search(stripped)
            if m:
                page = int(m.group(1))
        if equation is None:
            m = _GL.search(stripped) or _HASH_IMS.search(stripped)
            if m:
                equation = (
                    m.group(1)
                    if _GL.search(stripped)
                    else f"{m.group(1)}.{m.group(2)}"
                )
        i -= 1
        scanned += 1
    return {"german_page": page, "comment_equation": equation}


def parse_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tree = ast.parse(text)
    entries: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not _is_fromdfs(node.value):
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        var = target.id
        kw = _kwargs(node.value)
        dfs = _const_str(kw.get("s"))
        name = _const_str(kw.get("name"))
        ctx = _scan_preceding_comments(lines, node.lineno)
        equation = _equation_from(var, name) or ctx["comment_equation"]
        entries.append(
            {
                "file": str(path.relative_to(REPO_ROOT)),
                "variable": var,
                "equation_id": equation,
                "german_page": ctx["german_page"],
                "rule_name": name,
                "dfs": dfs,
            }
        )
    return entries


def build_index(files: list[Path]) -> dict:
    entries: list[dict] = []
    for path in files:
        if path.exists():
            entries.extend(parse_file(path))
        else:
            print(f"WARN: missing {path}")

    by_equation: dict[str, list[str]] = {}
    for e in entries:
        eq = e["equation_id"]
        if eq:
            by_equation.setdefault(eq, []).append(e["variable"])

    return {
        "generated_from": [str(p.relative_to(REPO_ROOT)) for p in files],
        "n_rules": len(entries),
        "n_equations": len(by_equation),
        "n_rules_without_equation": sum(
            1 for e in entries if not e["equation_id"]
        ),
        "by_equation": dict(sorted(by_equation.items())),
        "entries": entries,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--files", nargs="+", type=Path, default=DEFAULT_FILES)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    index = build_index(args.files)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(
        f"{index['n_rules']} rules, {index['n_equations']} equations, "
        f"{index['n_rules_without_equation']} without an equation id -> {args.out}"
    )


if __name__ == "__main__":
    main()
