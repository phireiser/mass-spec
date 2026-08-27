"""
Build mod.Rule fragmentation rules from the curated data/mechanisms corpus.

This is the shared conversion/validation pipeline (:func:`iter_conversions`)
behind two callers:

* ``python -m src.data_generation.mechanisms.build_rules`` -- prints a
  conversion/skip report and exits; nothing is written to disk.
* ``write_generated_rules.py`` -- writes the SAME rules out as a static
  ``generated_rules.py`` module, which is what
  ``src/data_generation/mechanisms/__init__.py`` (and therefore
  ``main.py --rule-source mechanisms``) actually imports. Run THAT (not this
  module) to refresh what a real build uses.

Both must run inside the project container -- ``mod`` is required. Each
convertible ``ElementaryStep`` becomes one rule, named
``"<mechanism_id>:<step_id>"``, at the same one-step-one-rule granularity as
the hand-authored ``_stepN`` rules in
``src/data_generation/rules/IMS_chap8_examples.py``.

A step is skipped, not converted, when:

* its own machine chemistry check (``MechanismRecord.validate_chemistry``)
  reports unbalanced atoms/charge/electrons -- typically a step drawn with an
  external reagent or proton not captured as a mapped species in the record;
* :func:`~.dfs_writer.reaction_dfs_string` cannot express it (an unmapped
  atom, an atom created/destroyed outright, or an implicit hydrogen moving
  without its own atom map -- see that module's docstring); or
* the resulting rule fails the same atom/charge/spin conservation guard
  ``src/data_generation/rules/__init__.py`` applies to the hand-authored
  rules -- kept as a second, independent line of defence against a
  SMIRKS->DFS converter bug, since there is no local ``mod`` install to test
  the converter's output against directly (see dfs_writer.py's docstring).

Every skip is recorded with a reason rather than silently dropped.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

import mod

from src.mechanisms.schema import MechanismRecord
from src.project_paths import shared_path

from .dfs_writer import (
    MechanismConversionError,
    apply_localization,
    compile_parsed_state,
    mapped_smiles_charge_and_radical,
    parse_mapped_smiles,
)

RECORDS_DIR = shared_path("MECHANISM_RECORDS_DIR_REL")


@dataclass
class SkippedStep:
    mechanism_id: str
    step_id: str
    reason: str

    def __str__(self) -> str:
        return f"{self.mechanism_id}:{self.step_id} -- {self.reason}"


@dataclass
class ConvertedStep:
    name: str           # "<mechanism_id>:<step_id>"
    dfs: str            # the compiled "reactants>>products" DFS string
    rule: "mod.Rule"
    auto_localized: bool = False  # reactant charge/radical reconstructed from the product
    inferred_h_moves: int = 0     # unmapped H relocations reconciled (see plan_implicit_hydrogens)


def _step_chemistry_defect(record: MechanismRecord, step_id: str) -> "str | None":
    """None if the step's machine chemistry check passes; else a reason string."""
    report = next(r for r in record.validate_chemistry() if r.step_id == step_id)
    problems = []
    if not report.atoms_balanced:
        problems.append("atoms not balanced")
    if not report.charge_balanced:
        problems.append("charge not balanced")
    if not report.total_electrons_balanced:
        problems.append("total electrons not balanced")
    return "; ".join(problems) if problems else None


def _label_charge_spin(string_label: str) -> Tuple[str, int, int]:
    """(undecorated symbol, formal charge, unpaired count) from a mod vertex label.

    Deliberately duplicated (not imported) from
    ``src.data_generation.rules._label_charge_spin``: it is a tiny pure
    function, and keeping this package's conservation guard independent of
    ``rules`` means a bug in one converter/guard cannot be masked or broken by
    an unrelated change to the other.
    """
    i = 0
    while i < len(string_label) and string_label[i] not in "+-.":
        i += 1
    symbol, deco = string_label[:i], string_label[i:]
    return symbol, deco.count("+") - deco.count("-"), deco.count(".")


def _conservation_defect(rule: "mod.Rule") -> "str | None":
    """None if ``rule`` conserves atoms/charge/spin left->right, else a reason."""
    def tally(side) -> Tuple[int, int, Dict[str, int]]:
        charge = spin = 0
        atoms: Dict[str, int] = {}
        for v in side.vertices:
            sym, ch, ra = _label_charge_spin(v.stringLabel)
            charge += ch
            spin += ra
            atoms[sym] = atoms.get(sym, 0) + 1
        return charge, spin, atoms

    lc, ls_, la = tally(rule.left)
    rc, rs, ra = tally(rule.right)
    reasons = []
    if la != ra:
        reasons.append("atoms")
    if lc != rc:
        reasons.append(f"charge {lc}->{rc}")
    if ls_ != rs:
        reasons.append(f"spin {ls_}->{rs}")
    return ", ".join(reasons) if reasons else None


def _localization_defect(species_in_state: list) -> "str | None":
    """None if every species' SMILES-localized charge/radical sums to that
    species' declared (species-level) totals; else a reason string.

    Catches, with a clear diagnosis, the case where a precursor is recorded
    with its charge/radical placed only at the species level and NOT on any
    atom in its SMILES -- by design for some sigma-ionized precursors under
    this project's delocalized-charge model (see
    ``dfs_writer.mapped_smiles_charge_and_radical``'s docstring) -- rather
    than letting it surface later as an opaque conservation-guard failure on
    the constructed mod rule.
    """
    for sp in species_in_state:
        charge, radical = mapped_smiles_charge_and_radical(sp.mapped_smiles)
        if charge != sp.charge or radical != sp.radical_electrons:
            return (
                f"species {sp.species_id!r} charge/radical is not localized "
                f"on any atom in its SMILES (SMILES sums to charge={charge}, "
                f"radical={radical}; species record declares charge="
                f"{sp.charge}, radical={sp.radical_electrons}) -- a mod rule "
                "needs a concretely-localized left/right graph, so this step "
                "cannot become a rule as recorded"
            )
    return None


def _fully_unlocalized(species_in_state: list) -> bool:
    """True if EVERY species in the state has zero charge/radical anywhere in
    its own SMILES -- the specific, narrow case
    :func:`~.dfs_writer.apply_localization` is safe for (a fully delocalized
    precursor, matching this project's own delocalized-charge model). False
    if some atoms ARE localized but the totals still don't sum right, which
    is a different, not-auto-fixable problem and must not be papered over."""
    for sp in species_in_state:
        charge, radical = mapped_smiles_charge_and_radical(sp.mapped_smiles)
        if charge != 0 or radical != 0:
            return False
    return True


def iter_conversions(
    records_dir: Path = RECORDS_DIR,
) -> "Iterator[ConvertedStep | SkippedStep]":
    """Walk every JSON record in ``records_dir`` and, per step, yield either a
    :class:`ConvertedStep` (converted, mod-validated, conservation-checked) or
    a :class:`SkippedStep` with the reason. The single shared pipeline behind
    both :func:`build_mechanism_rules` (in-memory rules for
    ``mechanisms/__init__.py``) and ``write_generated_rules.py`` (the
    ``generated_rules.py`` static-file writer), so the two can never drift
    apart on which steps are considered convertible.
    """
    for path in sorted(records_dir.glob("*.json")):
        try:
            record = MechanismRecord.from_json_file(path)
        except Exception as exc:  # malformed record; report and move on
            yield SkippedStep(path.stem, "*", f"could not load record: {exc}")
            continue

        for step in record.steps:
            defect = _step_chemistry_defect(record, step.step_id)
            if defect:
                yield SkippedStep(record.mechanism_id, step.step_id, defect)
                continue

            from_species = record.species_in_state(step.from_state)
            to_species = record.species_in_state(step.to_state)
            left_smiles = ".".join(sp.mapped_smiles for sp in from_species)
            right_smiles = ".".join(sp.mapped_smiles for sp in to_species)

            # The PRODUCT side must already be properly localized -- there is
            # nothing further downstream to reconstruct it from.
            to_defect = _localization_defect(to_species)
            if to_defect:
                yield SkippedStep(record.mechanism_id, step.step_id, to_defect)
                continue

            from_defect = _localization_defect(from_species)

            try:
                left_graph, left_h = parse_mapped_smiles(left_smiles)
                right_graph, right_h = parse_mapped_smiles(right_smiles)
            except MechanismConversionError as exc:
                yield SkippedStep(record.mechanism_id, step.step_id, str(exc))
                continue

            auto_localized = False
            if from_defect:
                if not _fully_unlocalized(from_species):
                    # Some atoms ARE localized but the totals still disagree --
                    # a different problem than "delocalized as drawn"; don't guess.
                    yield SkippedStep(record.mechanism_id, step.step_id, from_defect)
                    continue

                apply_localization(left_graph, right_graph)
                expected_charge = sum(sp.charge for sp in from_species)
                expected_radical = sum(sp.radical_electrons for sp in from_species)
                patched_charge = sum(a.charge for a in left_graph.atoms.values())
                patched_radical = sum(a.radical_electrons for a in left_graph.atoms.values())
                if (patched_charge, patched_radical) != (expected_charge, expected_radical):
                    yield SkippedStep(
                        record.mechanism_id, step.step_id,
                        "reactant charge/radical could not be auto-localized from "
                        f"the product placement (patched sum charge={patched_charge}, "
                        f"radical={patched_radical}; declared charge={expected_charge}, "
                        f"radical={expected_radical}) -- the missing charge/radical "
                        "is not fully accounted for among the product's atoms that "
                        "persist into the reactant",
                    )
                    continue
                auto_localized = True

            try:
                dfs, n_moves = compile_parsed_state(left_graph, left_h, right_graph, right_h)
            except MechanismConversionError as exc:
                yield SkippedStep(record.mechanism_id, step.step_id, str(exc))
                continue

            name = f"{record.mechanism_id}:{step.step_id}"
            try:
                rule = mod.Rule.fromDFS(s=dfs, name=name)
            except Exception as exc:  # mod itself rejected the generated DFS string
                yield SkippedStep(
                    record.mechanism_id, step.step_id,
                    f"mod.Rule.fromDFS rejected the generated DFS ({exc}): {dfs}",
                )
                continue

            defect = _conservation_defect(rule)
            if defect:
                yield SkippedStep(
                    record.mechanism_id, step.step_id,
                    f"generated rule fails the atom/charge/spin conservation guard "
                    f"({defect}) -- either a SMIRKS->DFS converter bug, or a step "
                    "the curators themselves flagged as spin-non-conserving 'as "
                    "drawn' (see e.g. RESUME.md's eq 9.31 note on a channel that is "
                    f"formally spin-forbidden): {dfs}",
                )
                continue

            yield ConvertedStep(
                name=name, dfs=dfs, rule=rule,
                auto_localized=auto_localized, inferred_h_moves=n_moves,
            )


def build_mechanism_rules(
    records_dir: Path = RECORDS_DIR,
) -> Tuple[List["mod.Rule"], List[SkippedStep]]:
    """Return ``(fragmentation_rules, skipped_steps)`` built from every JSON
    record in ``records_dir``."""
    fragmentation: List[mod.Rule] = []
    skipped: List[SkippedStep] = []
    for item in iter_conversions(records_dir):
        if isinstance(item, SkippedStep):
            skipped.append(item)
        else:
            fragmentation.append(item.rule)
    return fragmentation, skipped


if __name__ == "__main__":
    converted = []
    skipped = []
    for item in iter_conversions():
        (skipped if isinstance(item, SkippedStep) else converted).append(item)

    n_auto = sum(1 for c in converted if c.auto_localized)
    n_moves = sum(1 for c in converted if c.inferred_h_moves)
    print(f"{len(converted)} mechanism-derived fragmentation rule(s) built "
          f"({n_auto} with an auto-localized precursor, {n_moves} with an "
          f"inferred hydrogen migration), {len(skipped)} step(s) skipped, "
          f"from {RECORDS_DIR}")
    for skip in skipped:
        print(f"  SKIP {skip}")
