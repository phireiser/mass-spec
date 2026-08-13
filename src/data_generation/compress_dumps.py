#!/usr/bin/env python3
"""One-time migration: compress the derivation dumps already on disk.

The corpus predates :mod:`src.data_generation.utils.codec`, so it sits uncompressed --
45 GB in ``data/processed`` plus ~30 GB across the ``PROCESSED_DIR_OVERRIDE`` A/B trees,
against a measured ~25x. Readers accept both forms, so this is pure reclamation: nothing
depends on it having run, and a tree can be left half-migrated indefinitely.

Same conventions as :mod:`rename_dumps_to_cas`, the other one-time migration here: a dry
run by default, ``--apply`` to actually touch anything.

Safety, in the order it matters:

* **The original is never removed before its round-trip is proven.** Each file is hashed
  while it is compressed, the compressed copy is then read back and hashed, and only a
  match permits the delete.
* **Idempotent and resumable.** A file that is already compressed is skipped, so the
  filesystem is the progress state -- no journal to corrupt. Kill it and rerun.
* **Interruptible.** SIGTERM/SIGINT stop it between files, never mid-file, so a SLURM
  time limit cannot land in the destructive window. It exits 0 and prints the resume
  command, which is just the same command again.
* **mtime is preserved**, because ``cost_model`` and ``build_cost_probe`` read dump
  timestamps against job logs.

Usage::

    python src/data_generation/compress_dumps.py                        # dry run, main tree
    python src/data_generation/compress_dumps.py --all-trees            # dry run, everything
    python src/data_generation/compress_dumps.py --apply --jobs 8
    python src/data_generation/compress_dumps.py --clean-partials --apply
"""

from __future__ import annotations

import argparse
import hashlib
import os
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from src.data_generation.utils import codec
from src.data_generation.utils.dump_naming import (
    DONE_SUFFIX,
    DUMP_BASE_SUFFIXES,
    dump_stems,
    read_done_marker,
    write_done_marker,
)
from src.project_paths import shared_name, shared_path

# Set by the signal handler, read between files. Never interrupts a file mid-write.
_STOP = False


def _request_stop(signum, _frame) -> None:
    global _STOP
    _STOP = True
    print(f"\n  signal {signum} received; finishing the current file then stopping...",
          file=sys.stderr)


def _hash_stream(handle, chunk: int = codec.CHUNK) -> tuple[str, int]:
    """blake2b digest and byte count of everything left in ``handle``."""
    digest = hashlib.blake2b(digest_size=16)
    total = 0
    while block := handle.read(chunk):
        digest.update(block)
        total += len(block)
    return digest.hexdigest(), total


@dataclass
class Stats:
    considered: int = 0
    compressed: int = 0
    skipped: int = 0
    failed: int = 0
    raw_bytes: int = 0
    stored_bytes: int = 0
    markers: int = 0
    errors: List[str] = field(default_factory=list)

    def merge(self, other: "Stats") -> None:
        self.considered += other.considered
        self.compressed += other.compressed
        self.skipped += other.skipped
        self.failed += other.failed
        self.raw_bytes += other.raw_bytes
        self.stored_bytes += other.stored_bytes
        self.markers += other.markers
        self.errors.extend(other.errors)


def compress_one(src: Path, apply: bool) -> tuple[Optional[int], Optional[int], Optional[str]]:
    """Compress ``src`` in place. Returns ``(raw_bytes, stored_bytes, error)``.

    ``raw_bytes`` is returned even for a dry run, so a dry run can report the real
    saving. Only a verified round-trip lets the original be deleted.
    """
    dest = codec.compressed_path(src)
    if dest == src:  # DUMP_CODEC=none -- nothing to do
        return None, None, None

    stat = src.stat()
    with open(src, "rb") as handle:
        source_digest, raw_bytes = _hash_stream(handle)
    if not apply:
        return raw_bytes, None, None

    try:
        codec.compress_file(src, src)
    except Exception as exc:  # noqa: BLE001 - one bad file must not stop the migration
        return raw_bytes, None, f"{src}: compress failed: {exc}"

    # Verify before destroying: read the compressed copy back and compare digests.
    try:
        with codec.open_read(dest) as handle:
            check_digest, check_bytes = _hash_stream(handle)
    except Exception as exc:  # noqa: BLE001
        dest.unlink(missing_ok=True)
        return raw_bytes, None, f"{src}: verify failed to read back: {exc}"

    if check_digest != source_digest or check_bytes != raw_bytes:
        dest.unlink(missing_ok=True)
        return raw_bytes, None, (f"{src}: ROUND-TRIP MISMATCH "
                                 f"({check_bytes}B/{check_digest} vs {raw_bytes}B/"
                                 f"{source_digest}); original left untouched")

    stored_bytes = dest.stat().st_size
    os.utime(dest, (stat.st_atime, stat.st_mtime))
    src.unlink()
    return raw_bytes, stored_bytes, None


def migrate_stem(dump_dir: Path, stem: str, apply: bool) -> Stats:
    """Compress both files of one dump, then refresh its ``.done`` payload."""
    stats = Stats()
    sizes: Dict[str, Optional[int]] = {}
    for base in DUMP_BASE_SUFFIXES:
        src = dump_dir / f"{stem}{base}"
        stats.considered += 1
        if not src.exists():
            # Already compressed (or genuinely absent); recover the size for the marker.
            stats.skipped += 1
            sizes[base] = _known_uncompressed_size(dump_dir, stem, base)
            continue
        raw, stored, error = compress_one(src, apply)
        sizes[base] = raw
        if error:
            stats.failed += 1
            stats.errors.append(error)
            continue
        if raw is not None:
            stats.raw_bytes += raw
        if stored is not None:
            stats.compressed += 1
            stats.stored_bytes += stored

    # Refresh the marker only when both sizes are known and nothing failed, so a partly
    # migrated stem keeps whatever its old marker said rather than gaining a wrong one.
    if apply and not stats.errors and (dump_dir / f"{stem}{DONE_SUFFIX}").exists():
        dmp, pkl = sizes.get(".dmp"), sizes.get(".pkl")
        if isinstance(dmp, int) and isinstance(pkl, int):
            write_done_marker(dump_dir, stem, dmp_bytes=dmp, pkl_bytes=pkl)
            stats.markers += 1
    return stats


def _known_uncompressed_size(dump_dir: Path, stem: str, base: str) -> Optional[int]:
    """Uncompressed size of an already-migrated file, from the marker or by counting."""
    payload = read_done_marker(dump_dir, stem) or {}
    recorded = payload.get("dmp_bytes" if base == ".dmp" else "pkl_bytes")
    if isinstance(recorded, int):
        return recorded
    try:
        with codec.open_read(dump_dir / f"{stem}{base}") as handle:
            return _hash_stream(handle)[1]
    except FileNotFoundError:
        return None


def clean_partials(dump_dir: Path, apply: bool) -> int:
    """Remove orphaned ``.part`` files a killed run may have left."""
    count = 0
    for path in dump_dir.glob("*.part"):
        count += 1
        print(f"  {'removing' if apply else 'would remove'} orphan {path.name}")
        if apply:
            path.unlink(missing_ok=True)
    return count


def migrate_dir(dump_dir: Path, apply: bool, jobs: int, limit: Optional[int]) -> Stats:
    stats = Stats()
    if not dump_dir.is_dir():
        return stats
    stems = sorted(dump_stems(dump_dir, suffix=".pkl") | dump_stems(dump_dir, suffix=".dmp"))
    if limit is not None:
        stems = stems[:limit]
    if not stems:
        return stats
    print(f"  {dump_dir}: {len(stems)} dumps")

    # Threads, not processes: the work is file I/O plus pyarrow's C++ codec, both of
    # which release the GIL, and a thread pool avoids paying the mod import per worker.
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = []
        for stem in stems:
            if _STOP:
                break
            futures.append(pool.submit(migrate_stem, dump_dir, stem, apply))
        for future in futures:
            stats.merge(future.result())
    return stats


def tree_dirs(processed_dir: Path) -> List[Path]:
    return [processed_dir / shared_name(key)
            for key in ("FWD_DIR_REL", "BWD_DIR_REL")]


def discover_trees(processed_dir: Path, all_trees: bool) -> List[Path]:
    """The processed trees to walk: just this one, or every sibling A/B tree too."""
    if not all_trees:
        return [processed_dir]
    parent, prefix = processed_dir.parent, processed_dir.name
    return sorted(p for p in parent.glob(f"{prefix}*") if p.is_dir())


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main() -> None:
    ap = argparse.ArgumentParser(description="Compress derivation dumps in place")
    ap.add_argument("--processed-dir", default=str(shared_path("PROCESSED_DIR_REL")),
                    help="processed tree to migrate (default: the corpus of record)")
    ap.add_argument("--all-trees", action="store_true",
                    help="also migrate sibling PROCESSED_DIR_OVERRIDE trees")
    ap.add_argument("--apply", action="store_true",
                    help="actually rewrite files (default: dry run)")
    ap.add_argument("--jobs", type=int, default=4, help="concurrent files (default: 4)")
    ap.add_argument("--limit", type=int, default=None,
                    help="stop after this many dumps per directory")
    ap.add_argument("--clean-partials", action="store_true",
                    help="also remove orphaned .part files from a killed run")
    args = ap.parse_args()

    signal.signal(signal.SIGTERM, _request_stop)
    signal.signal(signal.SIGINT, _request_stop)

    processed = Path(args.processed_dir)
    trees = discover_trees(processed, args.all_trees)
    if not trees:
        sys.exit(f"no processed tree at {processed}")

    mode = "APPLY" if args.apply else "DRY RUN (pass --apply to rewrite)"
    print(f"{mode}: codec={codec.active_codec()}  trees={len(trees)}\n")

    total = Stats()
    started = time.time()
    for tree in trees:
        print(f"{tree}")
        for dump_dir in tree_dirs(tree):
            if not dump_dir.is_dir():
                continue
            if args.clean_partials:
                clean_partials(dump_dir, args.apply)
            total.merge(migrate_dir(dump_dir, args.apply, args.jobs, args.limit))
        if _STOP:
            break

    elapsed = time.time() - started
    print(f"\n{'-' * 60}")
    print(f"considered {total.considered} files in {elapsed:.1f}s")
    if args.apply:
        print(f"compressed {total.compressed}, already done {total.skipped}, "
              f"failed {total.failed}, markers refreshed {total.markers}")
        if total.stored_bytes:
            print(f"{human(total.raw_bytes)} -> {human(total.stored_bytes)} "
                  f"({total.raw_bytes / total.stored_bytes:.1f}x)")
    else:
        print(f"would compress {total.considered - total.skipped} files "
              f"({human(total.raw_bytes)} uncompressed); {total.skipped} already done")
    for error in total.errors:
        print(f"  ERROR {error}", file=sys.stderr)
    if _STOP:
        print("\nstopped early; rerun the same command to resume", file=sys.stderr)
    if total.failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
