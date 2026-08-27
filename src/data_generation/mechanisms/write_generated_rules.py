"""
Write the mechanism-derived fragmentation rules as a plain, static .py module.

    python -m src.data_generation.mechanisms.write_generated_rules

writes ``src/data_generation/mechanisms/generated_rules.py``: one
``mod.Rule.fromDFS(...)`` assignment per curated step that converts (see
``build_rules.iter_conversions`` for the shared validation pipeline: chemistry
balance, SMIRKS->DFS conversion, mod acceptance, conservation guard), in the
same style as the hand-authored files in ``src/data_generation/rules`` --
inspectable, greppable, and diffable like those, and importable without
re-deriving every rule from the curated JSON + RDKit + mod on every run.

Run this INSIDE THE PROJECT CONTAINER (``mod`` is required, and it is what
actually validates every generated DFS string -- this is the step that turns
"my converter thinks this is right" into "mod accepted it"). Re-run it
whenever ``data/mechanisms/records/*.json`` or ``dfs_writer.py`` changes;
the output file says so at the top and is otherwise never hand-edited.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.project_paths import shared_path

from .build_rules import ConvertedStep, SkippedStep, iter_conversions

DEFAULT_OUT = Path(__file__).with_name("generated_rules.py")

_NON_IDENTIFIER = re.compile(r"\W+")


def _safe_identifier(name: str) -> str:
    """"IMS4-EQ4.13:step_alpha_cleavage" -> "IMS4_EQ4_13_step_alpha_cleavage"."""
    ident = _NON_IDENTIFIER.sub("_", name).strip("_")
    if not ident or ident[0].isdigit():
        ident = f"_{ident}"
    return ident


def _dedupe(identifier: str, seen: "dict[str, int]") -> str:
    """Disambiguate an identifier that collides after sanitization (distinct
    names can map to the same identifier only if they differ solely in
    characters _safe_identifier collapses, which does not happen for this
    corpus's "<mechanism_id>:<step_id>" names, but a rename must not produce
    two module-level assignments silently shadowing each other)."""
    count = seen.get(identifier, 0)
    seen[identifier] = count + 1
    return identifier if count == 0 else f"{identifier}_{count}"


def write_generated_rules_file(
    out_path: Path = DEFAULT_OUT,
    records_dir: Path = shared_path("MECHANISM_RECORDS_DIR_REL"),
) -> "tuple[list[ConvertedStep], list[SkippedStep]]":
    """Write ``out_path``; return (converted steps, skipped steps)."""
    converted: "list[ConvertedStep]" = []
    skipped: "list[SkippedStep]" = []
    identifiers: "dict[str, str]" = {}  # name -> identifier
    seen: "dict[str, int]" = {}

    for item in iter_conversions(records_dir):
        if isinstance(item, SkippedStep):
            skipped.append(item)
            continue
        assert isinstance(item, ConvertedStep)
        converted.append(item)
        identifiers[item.name] = _dedupe(_safe_identifier(item.name), seen)

    lines = [
        '"""',
        "GENERATED FILE -- do not hand-edit.",
        "",
        "Compiled from the curated mechanism corpus in data/mechanisms/records by:",
        "",
        "    python -m src.data_generation.mechanisms.write_generated_rules",
        "",
        "Each rule is the FULL, CONCRETE reactant/product graph from one curated",
        "book example (not a generalized template like src/data_generation/rules --",
        "see src/data_generation/mechanisms/__init__.py for what that means in",
        "practice). A rule tagged 'auto-localized precursor' or 'N hydrogen",
        "migration(s) inferred' below had its reactant reconstructed from the",
        "product/curated data rather than read verbatim off the record's own",
        "reactant SMILES -- see build_rules.py's iter_conversions for exactly how",
        "and why that reconstruction is safe. Regenerate after editing",
        "data/mechanisms/records/*.json or src/data_generation/mechanisms/",
        "dfs_writer.py; do not edit by hand, changes will be silently overwritten",
        "by the next regeneration.",
        '"""',
        "import mod",
        "",
    ]
    for item in converted:
        identifier = identifiers[item.name]
        tags = []
        if item.auto_localized:
            tags.append("auto-localized precursor")
        if item.inferred_h_moves:
            tags.append(f"{item.inferred_h_moves} hydrogen migration(s) inferred")
        comment = f"# {item.name}" + (f"  [{', '.join(tags)}]" if tags else "")
        lines.append(comment)
        lines.append(f"{identifier} = mod.Rule.fromDFS(")
        lines.append(f"    s={item.dfs!r},")
        lines.append(f"    name={item.name!r},")
        lines.append(")")
        lines.append("")

    lines.append("fragmentation = [")
    for item in converted:
        lines.append(f"    {identifiers[item.name]},")
    lines.append("]")
    lines.append("")
    lines.append('__all__ = ["fragmentation"]')
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return converted, skipped


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    converted, skipped = write_generated_rules_file(out_path=args.out)
    n_auto = sum(1 for c in converted if c.auto_localized)
    n_moves = sum(1 for c in converted if c.inferred_h_moves)
    print(f"{len(converted)} rule(s) written to {args.out} "
          f"({n_auto} with an auto-localized precursor, {n_moves} with an "
          f"inferred hydrogen migration), {len(skipped)} step(s) skipped")
    for skip in skipped:
        print(f"  SKIP {skip}")


if __name__ == "__main__":
    main()
