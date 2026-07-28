"""
Validate curated mechanism records against the schema + basic chemistry.

Loads every ``*.json`` under a records directory, parses it with ``MechanismRecord``
(structure, ID uniqueness, reference integrity, DAG acyclicity), then runs
``validate_chemistry()`` on each. A record FAILS the gate if any step is not
atom/charge/total-electron balanced, has incomplete/duplicated atom maps, or has an
inconsistent radical parity -- the same invariant the MØD conservation guardrail enforces.
Electron-arrow endpoint mismatches, MS-context incoherence (convention G: an ``[M]+.`` adduct on
an even-electron fragment precursor), and other soft ``warnings`` are reported but only fail the
gate under ``--strict``.

Runs INSIDE the container (needs pydantic + rdkit):

    apptainer exec --bind "$PWD:/app" --env PYTHONPATH=/app mol-spectro.sif \\
        python /app/src/mechanisms/validate_records.py --records-dir /app/data/mechanisms/records

Exit code 0 = all pass, 1 = at least one failure (CI-friendly).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arrow_check import check_record_arrows  # noqa: E402
from schema import MechanismRecord  # noqa: E402

HARD_FLAGS = [
    "atoms_balanced",
    "charge_balanced",
    "total_electrons_balanced",
    "atom_maps_complete_and_unique",
    "radical_parity_consistent_before",
    "radical_parity_consistent_after",
]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RECORDS = REPO_ROOT / "data/mechanisms/records"


def check_ms_context(record: MechanismRecord) -> list[str]:
    """
    MS-context coherence (convention G): the ms_context must describe the species that
    actually undergoes the drawn reaction.

    ``adduct = "[M]+."`` claims the precursor IS the radical molecular ion, so it is only
    legitimate when the precursor species is odd-electron (charge +1, one unpaired electron).
    Chapter 8 is full of dissociations of *fragment* ions (even-electron oxonium/acylium
    daughters, CAD/MI-selected ions); tagging those ``[M]+.`` silently misdescribes the
    experiment. Conservation and arrow bookkeeping cannot see this class of error.

    Soft-only: returns advisory strings, never fails the gate on its own.
    """
    problems: list[str] = []
    ms = record.ms_context
    if ms is None:
        return problems

    precursors = [s for s in record.species if s.role.value == "precursor_ion"]
    if not precursors:
        return problems
    p = precursors[0]
    is_odd_electron = p.charge == 1 and p.radical_electrons == 1

    if ms.adduct and "[M]+" in ms.adduct and not is_odd_electron:
        problems.append(
            f"ms_context.adduct={ms.adduct!r} claims the radical molecular ion, but precursor "
            f"{p.species_id!r} is charge={p.charge}/radical_electrons={p.radical_electrons} "
            "(even-electron fragment) -- expected adduct=null (convention G)"
        )

    return problems


def check_record(
    path: Path, strict: bool, arrows: bool = True
) -> tuple[bool, list[str]]:
    problems: list[str] = []
    try:
        record = MechanismRecord.from_json_file(path)
    except Exception as exc:  # pydantic/JSON/structure errors
        return False, [f"load/validate error: {exc}"]

    for report in record.validate_chemistry():
        for flag in HARD_FLAGS:
            if not getattr(report, flag):
                problems.append(f"step {report.step_id}: {flag} = False")
        for warning in report.warnings:
            msg = f"step {report.step_id}: WARN {warning}"
            if strict:
                problems.append(msg)
            else:
                problems.append(f"(soft) {msg}")

    # Do the drawn arrows actually produce the product? (faithful electron-pushing)
    if arrows:
        for step_id, issues in check_record_arrows(record).items():
            for issue in issues:
                if issue.startswith("(soft)"):
                    problems.append(f"(soft) step {step_id}: ARROW {issue[7:]}")
                else:
                    problems.append(f"step {step_id}: ARROW {issue}")

    # Does the ms_context describe the species that actually reacts? (convention G)
    for issue in check_ms_context(record):
        msg = f"MS-CONTEXT {issue}"
        problems.append(msg if strict else f"(soft) {msg}")

    hard = [p for p in problems if not p.startswith("(soft)")]
    return (len(hard) == 0), problems


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--records-dir", type=Path, default=DEFAULT_RECORDS)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Treat soft warnings (arrow endpoints, smirks) as failures too.",
    )
    ap.add_argument(
        "--no-arrow-check",
        action="store_true",
        help="Skip the electron-move <-> bond-order bookkeeping gate.",
    )
    args = ap.parse_args()

    files = sorted(args.records_dir.glob("*.json"))
    if not files:
        print(f"No records found under {args.records_dir}")
        raise SystemExit(0)

    passed = failed = 0
    for path in files:
        ok, problems = check_record(path, args.strict, not args.no_arrow_check)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {path.name}")
        for p in problems:
            print(f"         {p}")
        passed += ok
        failed += not ok

    print(f"\n{passed}/{len(files)} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
