"""How derivation dumps are named, in one place.

CAS registry number is the single identifier: ``main.py --name-by-cas`` writes
every fwd/bwd dump under it, and it is the Parquet store's primary key. Dumps
written before that rename still carry the human name from ``compounds.csv``, so
every reader must try CAS first and fall back to the name.

That two-step was reimplemented in four call sites with three different spellings
(``run_ceiling._dump_stems``, ``machine_learning.main._dump_stem``,
``validate_migration_cap`` and ``analyze``). This module owns it instead.

Deliberately free of ``mod``: resolution is identifier bookkeeping plus a file
existence check, so it stays cheap and testable without a derivation graph.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence

from .spect_jdx import get_cas_by_smiles

# A dump is this trio; ``.done`` is written last as the completion marker.
DUMP_SUFFIXES = (".pkl", ".dmp", ".done")


def dump_stem_candidates(name: str, cas: object = None) -> List[str]:
    """Stems to try for a molecule, CAS first then the legacy human name.

    Empty/None entries are dropped, and the order is significant: CAS is the
    current identifier, the name is only a fallback for pre-rename dumps.
    """
    seen: List[str] = []
    for candidate in (cas, name):
        stem = str(candidate).strip() if candidate is not None else ""
        if stem and stem not in seen:
            seen.append(stem)
    return seen


def find_dump_stem(
    candidates: Sequence[str],
    dump_dir: Path | str,
    suffix: str = ".dmp",
) -> Optional[str]:
    """First candidate that has a dump in ``dump_dir``, or ``None``.

    ``suffix`` selects what counts as present: ``.dmp`` (the graph, the default)
    or ``.done`` to require a dump that finished writing.
    """
    directory = Path(dump_dir)
    for stem in candidates:
        if (directory / f"{stem}{suffix}").exists():
            return stem
    return None


def resolve_dump_stem(
    name: str,
    smiles: str,
    dump_dir: Path | str,
    parquet_dir: Path | str,
    suffix: str = ".dmp",
) -> Optional[str]:
    """Stem under which this molecule's dump actually exists, or ``None``.

    Looks the CAS up by SMILES, then takes the first candidate present on disk.
    A molecule absent from the store still resolves via its name, so this works
    for decoys and for anything not in NIST.
    """
    try:
        cas = get_cas_by_smiles(smiles, Path(parquet_dir))
    except Exception:  # noqa: BLE001 - a missing/unreadable store is not fatal
        cas = None
    return find_dump_stem(dump_stem_candidates(name, cas), dump_dir, suffix)


__all__ = [
    "DUMP_SUFFIXES",
    "dump_stem_candidates",
    "find_dump_stem",
    "resolve_dump_stem",
]
