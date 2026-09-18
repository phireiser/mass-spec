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


def _drop_isomorphic(converted: "list[ConvertedStep]") -> "tuple[list[ConvertedStep], list[tuple[str, str]]]":
    """Collapse rules that generalization made identical.

    Two book examples of the same reaction class converge on the same template
    once their spectator context is pruned -- 530 curated steps carry only
    ~220 distinct reactions at radius 0. Keeping all 530 would make mod match
    the same left graph many times over, and rule count is the variable the
    Phase-2 cost model is most sensitive to (docs/PHASE2_PLAN.md Stage 0).

    Returns ``(kept, [(dropped_name, duplicate_of_name), ...])``. Falls back to
    keeping everything if this mod build has no rule isomorphism check, since
    a redundant rule only costs time, while guessing at equality could drop a
    real reaction.
    """
    kept: "list[ConvertedStep]" = []
    dropped: "list[tuple[str, str]]" = []
    for item in converted:
        try:
            match = next(
                (k for k in kept if item.rule.isomorphism(k.rule, 1) > 0), None
            )
        except (AttributeError, TypeError) as exc:
            print(f"  NOTE: rule isomorphism unavailable ({exc}); keeping all "
                  f"{len(converted)} rules without deduplication")
            return converted, []
        if match is None:
            kept.append(item)
        else:
            dropped.append((item.name, match.name))
    return kept, dropped


def write_generated_rules_file(
    out_path: Path = DEFAULT_OUT,
    records_dir: Path = shared_path("MECHANISM_RECORDS_DIR_REL"),
    context_radius: "int | None" = None,
    spectator_hydrogens: bool = True,
    deduplicate: bool = True,
    placeholder_context: bool = False,
    bare_context_hydrogens: bool = False,
) -> "tuple[list[ConvertedStep], list[SkippedStep]]":
    """Write ``out_path``; return (converted steps, skipped steps).

    ``context_radius``/``spectator_hydrogens``/``placeholder_context`` are
    passed straight through to :func:`~.build_rules.iter_conversions` -- see
    :mod:`src.data_generation.mechanisms.generalize`.
    """
    converted: "list[ConvertedStep]" = []
    skipped: "list[SkippedStep]" = []
    identifiers: "dict[str, str]" = {}  # name -> identifier
    seen: "dict[str, int]" = {}

    for item in iter_conversions(
        records_dir,
        context_radius=context_radius,
        spectator_hydrogens=spectator_hydrogens,
        placeholder_context=placeholder_context,
        bare_context_hydrogens=bare_context_hydrogens,
    ):
        if isinstance(item, SkippedStep):
            skipped.append(item)
            continue
        assert isinstance(item, ConvertedStep)
        converted.append(item)

    duplicates: "list[tuple[str, str]]" = []
    if deduplicate and context_radius is not None:
        converted, duplicates = _drop_isomorphic(converted)
        if duplicates:
            print(f"  {len(duplicates)} step(s) generalized onto a rule already "
                  f"present and were dropped as isomorphic duplicates")
    for item in converted:
        identifiers[item.name] = _dedupe(_safe_identifier(item.name), seen)

    flags = ["python -m src.data_generation.mechanisms.write_generated_rules"]
    if context_radius is not None:
        flags.append(f"        --context-radius {context_radius}")
    if not spectator_hydrogens:
        flags.append("        --no-spectator-hydrogens")
    if context_radius is not None and not deduplicate:
        flags.append("        --no-deduplicate")
    if placeholder_context:
        flags.append("        --placeholder-context")
    if bare_context_hydrogens:
        flags.append("        --bare-context-hydrogens")

    if context_radius is None:
        scope = [
            "Each rule is the FULL, CONCRETE reactant/product graph from one curated",
            "book example (not a generalized template like src/data_generation/rules --",
            "see src/data_generation/mechanisms/__init__.py for what that means in",
            "practice).",
        ]
    else:
        scope = [
            f"Each rule is GENERALIZED to context radius {context_radius}: the atoms the step's",
            "rewrite actually touches (its graph diff, unioned with the curated",
            "electron-pushing arrows), the paths connecting them, an anchor atom",
            f"carrying the ion's charge, and a {context_radius}-bond shell of surrounding context.",
            "Spectator scaffolding from the book's example compound is dropped, so one",
            "rule matches the reaction CLASS rather than the single molecule it was",
            "drawn on -- see src/data_generation/mechanisms/generalize.py for exactly",
            "what is kept and why.",
        ]
        if not spectator_hydrogens:
            scope.append(
                "Unchanged spectator hydrogens are not written, so a step drawn on a"
            )
            scope.append("methyl also matches a methylene.")
        if bare_context_hydrogens:
            scope.append(
                "Shell positions carry no unchanged hydrogens, so they no longer"
            )
            scope.append("pin the substitution pattern the book example drew.")
        if placeholder_context:
            scope.append(
                "Shell positions are written as the placeholder '[_A]' rather than"
            )
            scope.append(
                "the element the book example happened to draw there, the way the"
            )
            scope.append(
                "hand-authored rules do. utils.constrain.apply_constraints binds"
            )
            scope.append(
                "'_A' to the elements occurring in the molecule under attack."
            )
        if duplicates:
            scope.append("")
            scope.append(
                f"{len(duplicates)} further step(s) generalized onto a rule already listed"
            )
            scope.append("here and were dropped as isomorphic duplicates.")

    lines = [
        '"""',
        "GENERATED FILE -- do not hand-edit.",
        "",
        "Compiled from the curated mechanism corpus in data/mechanisms/records by:",
        "",
        *[f"    {flag}" for flag in flags],
        "",
        *scope,
        "",
        "A rule tagged 'auto-localized precursor' or 'N hydrogen migration(s)",
        "inferred' below had its reactant reconstructed from the product/curated",
        "data rather than read verbatim off the record's own reactant SMILES --",
        "see build_rules.py's iter_conversions for exactly how and why that",
        "reconstruction is safe. Regenerate after editing",
        "data/mechanisms/records/*.json or src/data_generation/mechanisms/",
        "{dfs_writer,generalize}.py; do not edit by hand, changes will be",
        "silently overwritten by the next regeneration.",
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
    ap.add_argument(
        "--context-radius", type=int, default=None, metavar="N",
        help="Generalize each rule to the reacting core plus an N-bond shell of "
             "context (0 = core and its connectors only). Omit to keep the fully "
             "concrete graph from the book example, which is what shipped before "
             "this flag existed. See generalize.py.",
    )
    ap.add_argument(
        "--no-spectator-hydrogens", dest="spectator_hydrogens",
        action="store_false",
        help="Write only hydrogens that move, so a rule drawn on a methyl also "
             "matches a methylene. The single largest generality gain.",
    )
    ap.add_argument(
        "--placeholder-context", action="store_true",
        help="Write shell positions as '[_A]' instead of naming their element, so "
             "a rule stops insisting the neighbour was the atom the book drew. "
             "Needs --context-radius (a radius of 0 has no shell, so no effect).",
    )
    ap.add_argument(
        "--bare-context-hydrogens", action="store_true",
        help="Drop the unchanged hydrogens on shell positions only, so such a "
             "position stops pinning an exact substitution. The per-atom form of "
             "--no-spectator-hydrogens; paired with --placeholder-context it is "
             "the hand-authored rules' bare '[_A]' idiom. Needs --context-radius.",
    )
    ap.add_argument(
        "--no-deduplicate", dest="deduplicate", action="store_false",
        help="Keep every converted step even when generalization made several of "
             "them the same rule (only meaningful with --context-radius).",
    )
    args = ap.parse_args()

    converted, skipped = write_generated_rules_file(
        out_path=args.out,
        context_radius=args.context_radius,
        spectator_hydrogens=args.spectator_hydrogens,
        deduplicate=args.deduplicate,
        placeholder_context=args.placeholder_context,
        bare_context_hydrogens=args.bare_context_hydrogens,
    )
    n_auto = sum(1 for c in converted if c.auto_localized)
    n_moves = sum(1 for c in converted if c.inferred_h_moves)
    print(f"{len(converted)} rule(s) written to {args.out} "
          f"({n_auto} with an auto-localized precursor, {n_moves} with an "
          f"inferred hydrogen migration), {len(skipped)} step(s) skipped")
    if converted and args.context_radius is not None:
        mean_core = sum(c.n_core_atoms for c in converted) / len(converted)
        mean_written = sum(c.n_written_atoms for c in converted) / len(converted)
        mean_pruned = sum(c.n_pruned_atoms for c in converted) / len(converted)
        print(f"  generality: mean {mean_core:.1f} reacting atom(s) per rule, "
              f"{mean_written:.1f} atom(s) written, {mean_pruned:.1f} spectator "
              f"atom(s) pruned")
        if args.placeholder_context or args.bare_context_hydrogens:
            mean_shell = sum(c.n_shell_atoms for c in converted) / len(converted)
            acted = " and ".join(
                w for w, on in (("element-free", args.placeholder_context),
                                ("hydrogen-free", args.bare_context_hydrogens)) if on
            )
            print(f"  {mean_shell:.1f} context position(s) per rule written "
                  f"{acted}")
    for skip in skipped:
        print(f"  SKIP {skip}")


if __name__ == "__main__":
    main()
