"""Transparent compression for the derivation-dump files, in one place.

Dumps are dominated by redundancy -- the ``.pkl`` is a pickle of GML *text* and the
``.dmp`` is mod's binary serialisation of mostly small repeated integers -- so they
compress 18-90x. The corpus of record was 45 GB uncompressed.

**Codec: zstd, via pyarrow.** The container ships no ``zstandard`` module, no ``zstd``
binary and no ``lz4``; it does ship pyarrow, whose bundled codecs include a working
zstd. That is why compression goes through ``pyarrow.CompressedInputStream`` /
``CompressedOutputStream`` rather than the more obvious third-party module. Note this
pyarrow's stream constructors take a codec *name*, not a ``pa.Codec``, so the level is
fixed at zstd's default (1). Level 1 already gives ~25x here, and it decompresses ~4x
faster than gzip -- which matters because training reads every forward dump.

**Writes are atomic.** Everything lands on ``<final>.part`` and is ``os.replace``d into
position, so a job killed by a SLURM time limit can never leave behind a file that looks
complete. This is what lets ``.done`` keep meaning "the pair was written in full".

**Reads are backward compatible.** ``resolve_read_path`` prefers the compressed file but
falls back to a legacy uncompressed one, so the 1426-molecule corpus written before this
existed is still found. That is load-bearing, not a courtesy: if ``--avoid-reprocessing``
stopped seeing those dumps, the next data-gen array would rebuild every molecule from
scratch and the multi-hour ones would hit the wall clock.

Deliberately free of ``mod`` (same reasoning as :mod:`dump_naming`): compression is byte
plumbing, so it stays testable without building a derivation graph.

Set ``DUMP_CODEC=none`` to write uncompressed and turn this layer into a pass-through.
It is an environment knob rather than a ``paths.env`` key because ``paths.env`` holds
filesystem paths only.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pyarrow as pa

# Environment knobs. Read per call rather than cached at import so a test (or a single
# job) can flip them without reimporting the module.
CODEC_ENV = "DUMP_CODEC"
SCRATCH_ENV = "DUMP_SCRATCH"
DEFAULT_CODEC = "zstd"

# Codec name -> the suffix appended to the logical filename. "none" maps to the empty
# suffix, which makes every helper here a pass-through.
CODEC_SUFFIXES = {"zstd": ".zst", "none": ""}

# Streamed in 4 MiB blocks so peak memory stays flat regardless of dump size. The
# largest .dmp in the corpus is 770 MB and data-gen runs under --mem=16G.
CHUNK = 4 << 20


def active_codec() -> str:
    """The configured codec name, validated."""
    name = os.environ.get(CODEC_ENV) or DEFAULT_CODEC
    if name not in CODEC_SUFFIXES:
        raise ValueError(
            f"{CODEC_ENV}={name!r} is not supported; "
            f"expected one of {sorted(CODEC_SUFFIXES)}"
        )
    return name


def codec_suffix() -> str:
    """Suffix the active codec appends to a logical dump filename (``''`` if none)."""
    return CODEC_SUFFIXES[active_codec()]


def compressed_path(base: Path | str) -> Path:
    """Where a *new* write of ``base`` goes under the active codec."""
    return Path(str(base) + codec_suffix())


def resolve_read_path(base: Path | str) -> Path:
    """The file to actually read for logical name ``base``.

    Prefers ``base`` + the active codec's suffix, then any other known codec suffix,
    then the legacy uncompressed ``base`` itself. Raises ``FileNotFoundError`` listing
    what it tried if none exist -- a bare "no such file: x.pkl" would be misleading now
    that the real file on disk is usually ``x.pkl.zst``.
    """
    tried = []
    for suffix in _candidate_suffixes():
        candidate = Path(str(base) + suffix)
        tried.append(str(candidate))
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"no dump file for {base}; tried: {', '.join(tried)}")


def exists(base: Path | str) -> bool:
    """True iff some readable form of ``base`` is on disk (compressed or legacy)."""
    return any(Path(str(base) + s).exists() for s in _candidate_suffixes())


def _candidate_suffixes() -> list[str]:
    """Read-time suffix precedence: active codec first, then the rest, legacy last."""
    active = codec_suffix()
    others = [s for s in CODEC_SUFFIXES.values() if s and s != active]
    return [s for s in (active, *others) if s] + [""]


def _codec_for_path(path: Path) -> str | None:
    """Codec that wrote ``path``, from its suffix; ``None`` for an uncompressed file."""
    for name, suffix in CODEC_SUFFIXES.items():
        if suffix and path.name.endswith(suffix):
            return name
    return None


@contextmanager
def open_read(base: Path | str) -> Iterator:
    """Binary reader for ``base``, decompressing transparently."""
    path = resolve_read_path(base)
    name = _codec_for_path(path)
    if name is None:
        with open(path, "rb") as handle:
            yield handle
    else:
        with pa.CompressedInputStream(str(path), name) as handle:
            yield handle


@contextmanager
def open_write(base: Path | str) -> Iterator:
    """Binary writer for ``base``, compressing transparently and atomically.

    The bytes go to ``<final>.part`` and are renamed into place only after the body
    completes, so an interrupted write leaves no file that a later run could mistake
    for a finished one.
    """
    final = compressed_path(base)
    part = Path(str(final) + ".part")
    part.parent.mkdir(parents=True, exist_ok=True)
    name = _codec_for_path(final)
    try:
        if name is None:
            with open(part, "wb") as handle:
                yield handle
        else:
            with pa.CompressedOutputStream(str(part), name) as handle:
                yield handle
        os.replace(part, final)
    except BaseException:
        part.unlink(missing_ok=True)
        raise


def compress_file(src: Path | str, base: Path | str) -> int:
    """Copy ``src`` into the compressed form of ``base``. Returns ``src``'s byte size.

    Used for the ``.dmp``, which mod insists on writing itself to a plain path, so it
    cannot be streamed straight into a compressed file the way the pickle can.
    """
    src = Path(src)
    with open(src, "rb") as reader, open_write(base) as writer:
        while chunk := reader.read(CHUNK):
            writer.write(chunk)
    return src.stat().st_size


def decompress_to(base: Path | str, dst: Path | str) -> int:
    """Materialise ``base`` uncompressed at ``dst``. Returns bytes written.

    ``mod.DG.load(f=...)`` takes a filename, not a stream, so a compressed ``.dmp`` has
    to hit a real file before it can be loaded.
    """
    dst = Path(dst)
    written = 0
    with open_read(base) as reader, open(dst, "wb") as writer:
        while chunk := reader.read(CHUNK):
            writer.write(chunk)
            written += len(chunk)
    return written


@contextmanager
def materialize(base: Path | str) -> Iterator[Path]:
    """A real uncompressed path for ``base``, for APIs that will not take a stream.

    ``mod.DG.load(f=...)`` is the reason this exists. A legacy uncompressed file is
    yielded **as-is, with no copy**, so reading the pre-compression corpus costs exactly
    what it costs today. A compressed one is expanded into scratch and removed on exit;
    ``DG.load`` reads eagerly and holds no descriptor afterwards, so that is safe.
    """
    path = resolve_read_path(base)
    if _codec_for_path(path) is None:
        yield path
        return
    with scratch_dir() as scratch:
        restored = scratch / Path(base).name
        decompress_to(path, restored)
        yield restored


def drop_stale_variants(base: Path | str) -> None:
    """Delete the forms of ``base`` that the active codec did not just write.

    Without this, rewriting a legacy dump would leave the uncompressed original beside
    the new compressed one -- readers would be correct (they prefer the compressed file)
    but the space saving would be zero.
    """
    keep = compressed_path(base)
    for suffix in {*CODEC_SUFFIXES.values(), ""}:
        candidate = Path(str(base) + suffix)
        if candidate != keep:
            candidate.unlink(missing_ok=True)


@contextmanager
def scratch_dir(prefix: str = "dgdump_") -> Iterator[Path]:
    """Temporary directory for uncompressed intermediates, removed on exit.

    Defaults to ``tempfile``'s choice, which under apptainer is the host's node-local
    ``/tmp`` (bound in by default, 8 TB). Keeping the big uncompressed intermediate off
    the shared filesystem is deliberate: the processed tree is network-backed and, in
    this checkout, inside a synced directory. Override with ``DUMP_SCRATCH``.
    """
    root = os.environ.get(SCRATCH_ENV) or None
    if root:
        Path(root).mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix=prefix, dir=root))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


__all__ = [
    "CODEC_ENV",
    "SCRATCH_ENV",
    "CODEC_SUFFIXES",
    "active_codec",
    "codec_suffix",
    "compressed_path",
    "resolve_read_path",
    "exists",
    "open_read",
    "open_write",
    "compress_file",
    "decompress_to",
    "materialize",
    "drop_stale_variants",
    "scratch_dir",
]
