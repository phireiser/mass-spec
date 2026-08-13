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

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from . import codec
from .spect_jdx import get_cas_by_smiles

# Written last, so its presence proves the pair before it was written in full.
DONE_SUFFIX = ".done"

# The logical files a dump is made of. ``.done`` is never compressed -- it is tiny, and
# leaving it plain keeps every ``glob("*.done")`` + ``Path.stem`` reader working
# untouched (``Path("x.pkl.zst").stem`` is ``"x.pkl"``, which would silently break them).
DUMP_BASE_SUFFIXES = (".pkl", ".dmp")

# Every filename a dump can occupy on disk, for whole-group globbing and renaming.
# Consumers strip these by length rather than via ``Path.stem``, so double extensions
# are safe here.
DUMP_SUFFIXES = tuple(
    base + variant
    for base in DUMP_BASE_SUFFIXES
    for variant in ("", *(s for s in codec.CODEC_SUFFIXES.values() if s))
) + (DONE_SUFFIX,)


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

    A compressed dump counts as present. Missing that is how a compression change
    would quietly tell ``--avoid-reprocessing`` that the whole corpus needs
    rebuilding, so the compressed form is checked alongside the plain one.
    """
    directory = Path(dump_dir)
    for stem in candidates:
        if suffix == DONE_SUFFIX:
            if (directory / f"{stem}{suffix}").exists():
                return stem
        elif codec.exists(directory / f"{stem}{suffix}"):
            return stem
    return None


def dump_stems(dump_dir: Path | str, suffix: str = ".pkl") -> set:
    """Every stem with a ``suffix`` file in ``dump_dir``, compressed or not.

    Replaces the ``{p.stem for p in dir.glob("*.pkl")}`` idiom, which breaks on a
    compressed dump: ``Path("108-88-3.pkl.zst").stem`` is ``"108-88-3.pkl"``, so the
    stem set would silently come back full of near-miss keys that match nothing.
    """
    directory = Path(dump_dir)
    if not directory.is_dir():
        return set()
    stems = set()
    for variant in ("", *(s for s in codec.CODEC_SUFFIXES.values() if s)):
        tail = suffix + variant
        stems.update(p.name[: -len(tail)] for p in directory.glob(f"*{tail}"))
    return stems


def write_done_marker(
    path: Path | str,
    stem: str,
    dmp_bytes: Optional[int] = None,
    pkl_bytes: Optional[int] = None,
) -> None:
    """Write the completion marker for ``stem``, carrying the uncompressed sizes.

    The marker is the last thing a dump writes, so its presence proves the pair
    before it is whole. It used to be zero bytes; it now carries a small JSON body
    because once the files are compressed their ``st_size`` no longer answers "how
    big is this derivation graph", which is what ``cost_model`` needs.
    """
    payload = {"codec": codec.active_codec(), "dmp_bytes": dmp_bytes, "pkl_bytes": pkl_bytes}
    (Path(path) / f"{stem}{DONE_SUFFIX}").write_text(json.dumps(payload) + "\n",
                                                     encoding="utf-8")


def read_done_marker(path: Path | str, stem: str) -> Optional[Dict]:
    """Marker payload for ``stem``, or ``None``.

    ``None`` covers both "no marker" and "a legacy zero-byte marker": the latter is
    still a valid completion marker, it just carries no sizes. Callers must not read
    an unparseable marker as an incomplete dump -- every pre-compression dump in the
    corpus has an empty one.
    """
    marker = Path(path) / f"{stem}{DONE_SUFFIX}"
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def dump_uncompressed_bytes(stem: str, dump_dir: Path | str) -> Tuple[int, str]:
    """Logical (uncompressed) size of ``stem``'s dump, and where the number came from.

    Returns ``(bytes, "done")`` when the marker carries the sizes, else
    ``(bytes, "stat")`` from the files on disk -- which for an unmigrated dump is
    exactly the pre-compression number, so legacy trees report identically.
    """
    directory = Path(dump_dir)
    payload = read_done_marker(directory, stem) or {}
    sizes = [payload.get("dmp_bytes"), payload.get("pkl_bytes")]
    if all(isinstance(s, int) for s in sizes):
        return sum(sizes), "done"
    return dump_stored_bytes(stem, directory), "stat"


def dump_file(stem: str, dump_dir: Path | str, suffix: str = ".dmp") -> Path:
    """The dump file on disk for ``stem``, or its logical name if it is absent.

    For naming a file in a log message, where "the compressed one if it exists" is
    what a reader wants to see and a missing file must not raise.
    """
    base = Path(dump_dir) / f"{stem}{suffix}"
    try:
        return codec.resolve_read_path(base)
    except FileNotFoundError:
        return base


def dump_stored_bytes(stem: str, dump_dir: Path | str) -> int:
    """Bytes ``stem``'s dump actually occupies on disk, compressed or not."""
    directory = Path(dump_dir)
    total = 0
    for base in DUMP_BASE_SUFFIXES:
        try:
            total += codec.resolve_read_path(directory / f"{stem}{base}").stat().st_size
        except FileNotFoundError:
            pass
    return total


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
    "DONE_SUFFIX",
    "DUMP_BASE_SUFFIXES",
    "DUMP_SUFFIXES",
    "dump_stem_candidates",
    "dump_file",
    "dump_stems",
    "dump_stored_bytes",
    "dump_uncompressed_bytes",
    "find_dump_stem",
    "read_done_marker",
    "resolve_dump_stem",
    "write_done_marker",
]
